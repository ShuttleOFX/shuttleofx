import config
from config import globalOfxPluginPath, pluginsStorage, catalogRootUri
from pyTuttle import tuttle
from processify import processify

import tempfile
import json
import requests
import logging
import time
import os
import sys
import subprocess
import argparse
import copy
import cache
import uuid


class ProgressHandle(tuttle.IProgressHandle):
    def __init__(self, renderSharedInfo):
        super(ProgressHandle, self).__init__()
        self.renderSharedInfo = renderSharedInfo

    def beginSequence(self):
        """Called before the beginning of the process
        """
        pass

    def setupAtTime(self):
        """Called when setting up an image
        """
        pass

    def processAtTime(self):
        """Called before processing an image
        """
        self.renderSharedInfo["status"] = 99

    def endSequence(self):
        """Called at the end of the process
        """
        pass


def configLocalPluginPath(ofxPluginPaths):
    tuttle.core().getPluginCache().addDirectoryToPath(globalOfxPluginPath)

    for ofxPluginPath in ofxPluginPaths:
        logging.info("ofxPluginPath:" + str(ofxPluginPath))
        tuttle.core().getPluginCache().addDirectoryToPath(str(ofxPluginPath))
    pluginCache = tuttle.core().getPluginCache()
    tuttle.core().getFormatter().setLogLevel_int(5)
    tuttle.core().preload(False)

    logging.debug('Number of Plugins:' + str(len(pluginCache.getPlugins())))


def loadGraph(scene):
    logging.warning("loadGraph : " + str(scene))
    tuttleGraph = tuttle.Graph()

    nodes = []
    for node in scene['nodes']:
        if node['plugin'] == 'reader':
            filename = next(p["value"] for p in node['parameters'] if p["id"] == "filename")
            nodePlugin = tuttle.getBestReader(str(filename))
            logging.warning("Auto reader choice: " + nodePlugin)
        elif node['plugin'] == 'writer':
            filename = next(p["value"] for p in node['parameters'] if p["id"] == "filename")
            nodePlugin = tuttle.getBestWriter(str(filename))
            logging.warning("Auto reader choice: " + nodePlugin)
        else:
            nodePlugin = str(node['plugin'])

        tuttleNode = tuttleGraph.createNode(nodePlugin)

        node['name'] = tuttleNode.getName()
        for parameter in node['parameters']:
            param = tuttleNode.getParam(str(parameter["id"]))

            # Remap unicode to str. TODO: check if it's still needed.
            if isinstance(parameter["value"], unicode):
                parameter["value"] = str(parameter["value"])

            if isinstance(parameter["value"], list):
                for i, v in enumerate(parameter["value"]):
                    param.setValueAtIndex(i, v, tuttle.eChangeUserEdited)
            else:
                param.setValue(parameter["value"], tuttle.eChangeUserEdited)
        nodes.append(tuttleNode)
        # logging.warning("tuttleNode: " + str(tuttleNode))

    for connection in scene['connections']:
        # TODO: replace src/dst with from/to.
        tuttleGraph.connect([
            nodes[connection['src']['id']],
            nodes[connection['dst']['id']],
        ])

    return tuttleGraph


@processify
def convertScenePatterns(scene):
    '''
    Replace PATTERNS with real filepaths.
    :param scene: dict with nodes, params and connections.
    :return: (scene, outputFilepaths)
    '''
    outputScene = copy.deepcopy(scene)
    # Preload general plugins to use getBestReader/getBestWriter.
    tuttle.core().getPluginCache().addDirectoryToPath(globalOfxPluginPath)
    tuttle.core().preload(False)
    logging.debug("outputScene: " + str(outputScene))

    outputResources = []
    for node in outputScene['nodes']:

        if 'plugin' in node and node['plugin'] is not 'reader':
            logging.debug("Retrieve bundleId from plugin: " + str(node['plugin']))
            resp = requests.get(catalogRootUri + "/bundle/" + node['plugin'] + '/bundle')
            if resp.status_code == 404:
              logging.warning("Cannont retrieve bundleId for plugin: " + str(node['plugin']))
            else:
              respJson = resp.json()
              node["bundleId"] = respJson['bundleId']
              logging.debug("bundleId: " + str(respJson['bundleId']))

        for parameter in node['parameters']:
            logging.warning('param: %s %s', parameter['id'], parameter['value'])
            if isinstance(parameter['value'], (str, unicode)):

                if 'plugin' not in node and '{RESOURCES_DIR}' in parameter['value']:
                    parameter['value'] = parameter['value'].replace('{RESOURCES_DIR}', config.resourcesPath)
                    node['plugin'] = tuttle.getBestReader(str(parameter['value']))

                if 'plugin' not in node and '{UNIQUE_OUTPUT_FILE}' in parameter['value']:
                    node['plugin'] = tuttle.getBestWriter(str(parameter['value']))

    # Declare Bundles paths to TuttleOFX
    bundleIds = []
    for node in outputScene['nodes']:
        if 'bundleId' in node:
            bundleIds.append(node['bundleId'])
        else:
            logging.error("No bundle defined for node: " + str(node))
    bundlePaths = [os.path.join(pluginsStorage, str(bundleId)) for bundleId in bundleIds]
    logging.debug("bundlePaths: " + str(bundlePaths))
    configLocalPluginPath(bundlePaths)

    logging.debug("outputScene after conversion: " + str(outputScene))

    # Create a Tuttle Graph to generate the UID for each node
    tuttleGraphTmp = loadGraph(outputScene)
    # logging.warning("tuttleGraphTemp" + str(tuttleGraphTmp))
    # logging.warning("outputScene" + str(outputScene))
    nodesHashMap = tuttle.NodeHashContainer()
    tuttleGraphTmp.computeGlobalHashAtTime(nodesHashMap, 0.0)

    for node in outputScene['nodes']:
        for parameter in node['parameters']:
            logging.warning('param: %s %s', parameter['id'], parameter['value'])
            if isinstance(parameter['value'], (str, unicode)):

                if '{UNIQUE_OUTPUT_FILE}' in parameter['value']:
                    prefix, suffix = parameter['value'].split('{UNIQUE_OUTPUT_FILE}')
                    nodeHash = str(nodesHashMap.getHash(node['name'], 0.0))
                    node['hash'] = nodeHash
                    filename = nodeHash + suffix
                    filepath = os.path.join(config.renderDirectory, cache.cachePathFromFile(filename))
                    outputResources.append(filename)
                    parameter['value'] = filepath

    return (outputScene, outputResources)


def computeGraph(renderSharedInfo, newRender, bundlePaths):
    try:
        renderSharedInfo['startDate'] = time.time()
        configLocalPluginPath(bundlePaths)

        renderSharedInfo['status'] = 1
        tuttleGraph = loadGraph(newRender['scene'])

        logging.error('tuttle graph:' + str(tuttleGraph))
        print('tuttle graph:' + str(tuttleGraph))

        renderSharedInfo['status'] = 2
        tuttleComputeOptions = tuttle.ComputeOptions()

        if 'options' in newRender['scene']:
            for option in newRender['scene']['options']:

                if "TimeRange" in option['id']:
                    begin = option['values']['begin']
                    end = option['values']['end']
                    step = option['values']['step']
                    tuttleComputeOptions.setTimeRange(begin, end, step)

                if "RenderScale" in option['id']:
                    x = option['values']['x']
                    y = option['values']['y']
                    tuttleComputeOptions.setRenderScale(x, y)

        ## Create handle and set it in ComputeOptions
        progressHandle = ProgressHandle(renderSharedInfo)
        tuttleComputeOptions.setProgressHandle(progressHandle)

        tuttleGraph.compute(tuttleComputeOptions)

        renderSharedInfo['status'] = 3

    except Exception as e:
        logging.error("_" * 80)
        logging.error(" " * 20 + "RENDER ERROR")
        logging.error(str(e))
        # logging.error("bundlePaths:", str(bundlePaths))
        # logging.error("tuttleGraph:", str(tuttleGraph))
        logging.error("_" * 80)
        renderSharedInfo['status'] = -1
        raise


def launchComputeGraph(renderSharedInfo, newRender):
    scene = newRender['scene']
    bundleIds = set([])
    for node in scene['nodes']:
        if 'bundleId' in node:
            bundleIds.add(node['bundleId'])
        else:
            logging.error("No bundle defined for node: " + str(node))

    name = '_'.join([node['plugin'].lower() for node in scene['nodes']])
    bundlePaths = [os.path.join(pluginsStorage, str(bundleId)) for bundleId in bundleIds]

    if False:
        # Direct call to the render function
        # Not used, just here for debug purpose.
        computeGraph(renderSharedInfo, newRender, bundlePaths)
    else:
        # Use a subprocess to render.
        # This allows to modify the LD_LIBRARY_PATH.
        _, tempFilepath = tempfile.mkstemp()
        renderArgs = {
            "renderSharedInfo": dict(renderSharedInfo),
            "newRender": dict(newRender),
            "bundlePaths": bundlePaths
        }
        jsonData = json.dumps(renderArgs, sort_keys=False, indent=4)
        open(tempFilepath, 'w').write(jsonData)

        logging.info('tempFilepath: %s', tempFilepath)

        env = dict(os.environ)
        env['LD_LIBRARY_PATH'] = ':'.join(
                [env.get('LD_LIBRARY_PATH', '')] + ['{bundlePath}/lib:{bundlePath}/lib64'.format(bundlePath=bundlePath)
                                                    for
                                                    bundlePath in bundlePaths])
        logging.info('LD_LIBRARY_PATH: %s', env['LD_LIBRARY_PATH'])
        
        codePath = os.path.dirname(os.path.abspath(__file__))
        name = 'shuttleofx_render_{uid}'.format(uid=uuid.uuid4())
        dockerargs = [
            '/usr/bin/timelimit', '-t', str(config.timeout_sec), '-T', str(config.timeout_sec),
            '/usr/bin/docker', 'run',
            # set cpu-shares to 1024 (the default value).
            # The main docker (for the server) use 4096 to ensure responsiveness.
            '--cpu-shares=1024',
            '--memory=500M',  # limit RAM
            '--memory-swap=-1',  # disable memory swap
            '--rm=true',  # Automatically remove the container => doesn't work with kill from timelimit
            '--net=none',  # disables all incoming and outgoing networking
            # Set a unique name
            '--name={name}'.format(name=name),
            # Give access to source code to execute in read-only
            # '-v', 'DEV_CODE_PATH:{codePath}:ro'.format(codePath=codePath),
            # '-w', '{codePath}'.format(codePath=codePath),  # set the workdir
            # Give access to the image cache
            # '-v', '{renderDirectory}:{renderDirectory}'.format(renderDirectory=config.renderDirectory),
            # Give access to the output json file
            '-v', '{tempFilepath}:{tempFilepath}'.format(tempFilepath=tempFilepath),
            # Give access to config files
            '-v', '/etc/shuttleofx:/etc/shuttleofx:ro',
            # TODO: use config instead of hardcoded paths
            # TODO: limit access to sub-directories
            '-v', '/opt/shuttleofx:/opt/shuttleofx',
            ]
        # Give access to the plugins themselves in read-only
        # for bundlePath in bundlePaths:
        #     dockerargs += ['-v', '{bundlePath}:{bundlePath}'.format(bundlePath=bundlePath)]
        # Name of the docker image (after all options)
        dockerargs.append(config.dockerImage)
        
        pyfile = os.path.abspath(__file__[:-1] if __file__.endswith('.pyc') else __file__)
        args = [sys.executable, pyfile, tempFilepath]
        logging.warning('dockerargs: %s', ' '.join(dockerargs))
        logging.warning('args: %s', ' '.join(args))

        p = subprocess.Popen(dockerargs + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdoutdata, stderrdata = p.communicate()

        # Remove the docker container
        # We do it manually instead of using --rm=true
        # to remove the container even if docker was killed by timelimit.
        subprocess.call(['/usr/bin/docker', 'rm', '-f', name])

        if p.returncode:
            renderSharedInfo['status'] = -1
            tmpData = ""
            try:
                tmpData = open(tempFilepath, 'r').read()
            except:
                pass
            raise RuntimeError(
                    '''Failed to render.\n
                    Return code: %s\n
                    Log:\n%s\n
                    Log err:\n%s\n
                    File data:\n%s\n'''
                    % (p.returncode, stdoutdata, stderrdata, tmpData))

        logging.info(stdoutdata)
        logging.info(stderrdata)

        os.remove(tempFilepath)

    renderSharedInfo['status'] = 3


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch the render.')
    parser.add_argument('renderArgs', type=str,
                        help='The file which contains the render arguments.')
    args = parser.parse_args()

    renderArgs = json.load(open(args.renderArgs, 'r'))
    computeGraph(**renderArgs)

    sys.exit(0)
