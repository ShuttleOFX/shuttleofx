import os
import shutil
import tarfile
import logging
import threading
import multiprocessing
import tempfile
import ConfigParser


from pyTuttle import tuttle
import Plugin


currentAppDir = os.path.dirname(__file__)

configParser =  ConfigParser.RawConfigParser()
configParser.read( os.path.join( currentAppDir, 'analyser.cfg' ) )
tmpRenderingPath = configParser.get('APP_ANALYSER', 'workingTmpDir')

if not os.path.exists(tmpRenderingPath):
    os.mkdir(tmpRenderingPath)

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
    Launches the analyse. Set the process status and fill sharedBundleDatas with the analysed bundle datas. Delete temporary files and directories created during the archive extraction.
    '''

    sharedBundleDatas['status'] = 'running'
    sharedBundleDatas['analyse'] = 'waiting'
    sharedBundleDatas['extraction'] = 'running'

    bundlePath = os.path.join( tmpRenderingPath, str(bundleId) )
    
    os.mkdir(bundlePath)

    if 'gzip' == bundleExt.split('/')[1]:
        extractDatasAsTar(bundleBin, bundlePath)
    elif 'zip' == bundleExt.split('/')[1]:
        extractDatasAsZip(bundleBin, bundlePath)
    sharedBundleDatas['extraction'] = 'done'

    analysedBundle = None
    sharedBundleDatas['analyse'] = 'running'
    analysedBundle = analyse(bundlePath)
    sharedBundleDatas['analyse'] = 'done'

    #shutil.rmtree(bundlePath)

    # print analysedBundle

    sharedBundleDatas['datas'] = analysedBundle
    sharedBundleDatas['status'] = 'done'
