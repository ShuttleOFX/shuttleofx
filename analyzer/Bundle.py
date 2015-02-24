import os
import shutil
import tarfile
import threading
import multiprocessing
import tempfile


from pyTuttle import tuttle
import plugin


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


def analyze(pluginPath):
    '''
    Analyze the bundle an return a description for each plugin.
    '''

    p = plugin.Plugin()
    pluginCache = tuttle.core().getPluginCache()
    pluginCache.addDirectoryToPath(pluginPath)
    tuttle.core().preload(False)
    plugins = pluginCache.getPlugins()

    pluginsDescription = {'plugins':[], 'total': len(plugins)}

    for currentPlugin in plugins:
        pluginsDescription['plugins'].append(p.getPluginProperties(currentPlugin))

    return pluginsDescription


def launchAnalyze(sharedBundleDatas, bundleExt, bundleBin, bundleId):
    '''
    Launches the analyze. Set the process status and fill sharedBundleDatas with the analyzed bundle datas. Delete temporary files and directories created during the archive extraction.
    '''

    sharedBundleDatas['globalStatus'] = 'running'
    sharedBundleDatas['analyzeStatus'] = 'waiting'
    sharedBundleDatas['extractionStatus'] = 'running'

    bundlePath = 'tmp/' + str(bundleId)
    os.mkdir(bundlePath)

    if 'gzip' == bundleExt.split('/')[1]:
        extractDatasAsTar(bundleBin, bundlePath)
    elif 'zip' == bundleExt.split('/')[1]:
        extractDatasAsZip(bundleBin, bundlePath)
    sharedBundleDatas['extractionStatus'] = 'done'

    analyzedBundle = None
    sharedBundleDatas['analyzeStatus'] = 'running'
    analyzedBundle = analyze(bundlePath)
    sharedBundleDatas['analyzeStatus'] = 'done'

    shutil.rmtree(bundlePath)

    sharedBundleDatas['datas'] = analyzedBundle
    sharedBundleDatas['globalStatus'] = 'done'
    

