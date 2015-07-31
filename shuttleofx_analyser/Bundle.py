import os
import sys
import shutil
import tarfile
import logging
import tempfile
import ConfigParser
import subprocess
import json
import argparse
import logging

from pyTuttle import tuttle
import Plugin

from shuttleofx_analyser import tmpRenderingPath

if not os.path.exists(tmpRenderingPath):
    os.makedirs(tmpRenderingPath)

def extractDatasAsTar(datas, outputPath):
    '''
    Extract bundle as a tar file.
    '''
    tempFilePath = outputPath + ".tar.gz"

    try:
        f = open(tempFilePath, 'w')
        f.write(datas)
        f.close()

        tar = tarfile.open(tempFilePath, mode='r')
        tar.extractall(outputPath)

        tar.close()
    except:
        print "error while extracting the tar.gz archive"
    else:
        os.remove(tempFilePath)


def extractDatasAsZip(datas, outputPath):
    '''
    Extract bundle as a zip file.
    '''

    tempFilePath = outputPath + ".zip"
    try:
        f = open(tempFilePath, 'w')
        f.write(datas)
        f.close()
    except:
        print "error while extracting the zip archive"
    else:
        os.remove(tempFilePath)
        raise NotImplementedError()
        # TODO : extract archive as zip


def analyse(pluginPath):
    '''
    Analyse the bundle an return a description for each plugin.
    '''

    pluginCache = tuttle.core().getPluginCache()
    pluginCache.addDirectoryToPath(str(pluginPath))
    tuttle.core().preload(False)
    plugins = pluginCache.getPlugins()

    logging.warning('pluginCache: %s' % pluginCache)
    logging.warning('Analyse plugins: %s' % pluginPath)
    logging.warning('Nb plugins: %s' % len(plugins))
    pluginsDescription = {'plugins':[], 'total': len(plugins)}

    for currentPlugin in plugins:
        logging.warning(currentPlugin.getRawIdentifier())
        p = Plugin.Plugin(currentPlugin)
        pluginsDescription['plugins'].append(p.__dict__)

    return pluginsDescription


def launchAnalyse(sharedBundleDatas, bundleExt, bundleBin, bundleId):
    '''
    Launches the analyse.
    Set the process status and fill sharedBundleDatas with the analysed bundle datas.
    Delete temporary files and directories created during the archive extraction.
    '''

    sharedBundleDatas['status'] = 'running'
    sharedBundleDatas['analyse'] = 'waiting'
    sharedBundleDatas['extraction'] = 'running'

    bundlePath = os.path.join(tmpRenderingPath, str(bundleId))

    os.mkdir(bundlePath)

    if 'gzip' == bundleExt.split('/')[1]:
        extractDatasAsTar(bundleBin, bundlePath)
    elif 'zip' == bundleExt.split('/')[1]:
        extractDatasAsZip(bundleBin, bundlePath)
    sharedBundleDatas['extraction'] = 'done'

    analysedBundle = None
    sharedBundleDatas['analyse'] = 'running'
    if False:
        # Direct call to the analyse function
        # Not used, just here for debug purpose.
        analysedBundle = analyse(bundlePath)
    else:
        # Use a subprocess to analyse the bundle.
        # This allows to modify the LD_LIBRARY_PATH.
        _, tempFilepath = tempfile.mkstemp()
        logging.warning('tempFilepath: %s', tempFilepath)

        env = dict(os.environ)
        # env['OFX_PLUGIN_PATH'] = bundlePath
        env['LD_LIBRARY_PATH'] = ':'.join([env.get('LD_LIBRARY_PATH', ''), '{bundlePath}/lib:{bundlePath}/lib64'.format(bundlePath=bundlePath)])
        logging.warning('LD_LIBRARY_PATH: %s', env['LD_LIBRARY_PATH'])

        args = [sys.executable, os.path.abspath(__file__), bundlePath, tempFilepath]
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdoutdata, stderrdata = p.communicate()
        if p.returncode:
            sharedBundleDatas['analyse'] = 'error'
            raise RuntimeError(
                '''Failed to analyse the Bundle "%s".\n
                Return code: %s\n
                Log:\n%s\n%s\n'''
                % (bundlePath, p.returncode, stdoutdata, stderrdata))

        logging.warning(stdoutdata)
        logging.warning(stderrdata)

        analysedBundle = json.load(open(tempFilepath, 'r'))
        logging.warning('analysedBundle: %s' % analysedBundle)
        # os.path.remove(tempFilepath)

    sharedBundleDatas['analyse'] = 'done'

    # print analysedBundle

    sharedBundleDatas['datas'] = analysedBundle
    sharedBundleDatas['status'] = 'done'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('bundlePath', type=str,
                       help='Path to the OFX bundle directory.')
    parser.add_argument('outputJsonFile', type=str,
                       help='Output JSON file with the analyse information.')
    args = parser.parse_args()

    data = analyse(args.bundlePath)
    jsonData = json.dumps(data, sort_keys=False, indent=4)
    open(args.outputJsonFile, 'w').write(jsonData)
    sys.exit(0)
