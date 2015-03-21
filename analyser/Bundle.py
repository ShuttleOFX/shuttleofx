import os
import shutil
import tarfile
import threading
import multiprocessing
import tempfile
import logging

from pyTuttle import tuttle
import Plugin


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
        logging.error("error while extracting the tar.gz archive")
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
        logging.error("error while extracting the zip archive")
    else:
        os.remove(tempFilePath)
        raise NotImplementedError()
        # TODO : extract archive as zip


def analyse(pluginPath):
    '''
    Analyse the bundle an return a description for each plugin.
    '''

    p = Plugin.Plugin()
    pluginCache = tuttle.core().getPluginCache()
    pluginCache.addDirectoryToPath(pluginPath)
    tuttle.core().preload(False)
    plugins = pluginCache.getPlugins()

    pluginsDescription = {'plugins':[], 'total': len(plugins)}

    for currentPlugin in plugins:
        pluginsDescription['plugins'].append(p.getPluginProperties(currentPlugin))

    return pluginsDescription


def launchAnalyse(sharedBundleDatas, bundleExt, bundleBin, bundleId):
    '''
    Launches the analyse. Set the process status and fill sharedBundleDatas with the analysed bundle datas. Delete temporary files and directories created during the archive extraction.
    '''

    sharedBundleDatas['status'] = 'running'
    sharedBundleDatas['analyse'] = 'waiting'
    sharedBundleDatas['extraction'] = 'running'
    bundlePath = None

    try:
        bundlePath = tempfile.mkdtemp()
        if 'gzip' == bundleExt.split('/')[1]:
            extractDatasAsTar(bundleBin, bundlePath)
        elif 'zip' == bundleExt.split('/')[1]:
            extractDatasAsZip(bundleBin, bundlePath)
        sharedBundleDatas['extraction'] = 'done'

        sharedBundleDatas['analyse'] = 'running'
        analysedBundle = analyse(bundlePath)
        sharedBundleDatas['analyse'] = 'done'
        sharedBundleDatas['datas'] = analysedBundle
        sharedBundleDatas['status'] = 'done'
    except:
        logging.error("Can't create tmp directory for analyse.")
    else:
        shutil.rmtree(bundlePath)

