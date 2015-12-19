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
    # logging.warning("loadGraph : " + str(scene))
    tuttleGraph = tuttle.Graph()


    nodes = []
    for node in scene['nodes']:
        tuttleNode = tuttleGraph.createNode(str(node['plugin']))
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
    tuttle.core().getPluginCache().addDirectoryToPath(globalOfxPluginPath)
    tuttle.core().preload(False)

    outputResources = []
    for node in outputScene['nodes']:
        for parameter in node['parameters']:
            logging.warning('param: %s %s', parameter['id'], parameter['value'])
            if isinstance(parameter['value'], (str, unicode)):

                if '{RESOURCES_DIR}' in parameter['value']:
                    parameter['value'] = parameter['value'].replace('{RESOURCES_DIR}', config.resourcesPath)
                    node['plugin'] = tuttle.getBestReader(str(parameter['value']))

    # Create a Tuttle Graph to generate the UID for each node
    tuttleGraphTmp = loadGraph(outputScene)
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
                    filepath = os.path.join(config.renderDirectory, filename)
                    outputResources.append(filename)
                    parameter['value'] = filepath

    return (outputScene, outputResources)


def computeGraph(renderSharedInfo, newRender, bundlePaths):
    try:
        renderSharedInfo['startDate'] = time.time()
        configLocalPluginPath(bundlePaths)

        renderSharedInfo['status'] = 1
        tuttleGraph = loadGraph(newRender['scene'])

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
        logging.error("_"*80)
        logging.error(" "*20 + "RENDER ERROR")
        logging.error(str(e))
        # logging.error("bundlePaths:", str(bundlePaths))
        # logging.error("tuttleGraph:", str(tuttleGraph))
        logging.error("_"*80)
        renderSharedInfo['status'] = -1
        raise


def launchComputeGraph(renderSharedInfo, newRender):
    scene = newRender['scene']
    bundleIds = []
    for node in scene['nodes']:
        if 'plugin' in node:
            resp = requests.get(catalogRootUri+"/bundle/" + node['plugin']+ '/bundle').json()
            bundleIds.append(resp['bundleId'])
        else:
            logging.error("No plugin defined for node: "+str(node))

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
        env['LD_LIBRARY_PATH'] = ':'.join([env.get('LD_LIBRARY_PATH', '')] + ['{bundlePath}/lib:{bundlePath}/lib64'.format(bundlePath=bundlePath) for bundlePath in bundlePaths])
        logging.info('LD_LIBRARY_PATH: %s', env['LD_LIBRARY_PATH'])

        args = [sys.executable, os.path.abspath(__file__), tempFilepath]
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdoutdata, stderrdata = p.communicate()
        if p.returncode:
            renderSharedInfo['status'] = -1
            raise RuntimeError(
                '''Failed to render.\n
                Return code: %s\n
                Log:\n%s\n%s\n'''
                % (p.returncode, stdoutdata, stderrdata))

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
