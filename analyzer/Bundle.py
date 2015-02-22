import os
import shutil
import tarfile
import threading
import multiprocessing
from multiprocessing import Process


from pyTuttle import tuttle
import plugin

def launchAnalyze(bundle, sharedBundleDatas, bundleExt, bundleBin, bundleId):
    '''
    Launches the analyze. Set the process status and fill sharedBundleDatas with the analyzed bundle datas. Delete temporary files and directories created during the archive extraction.
    '''
    sharedBundleDatas["status"] = "start extraction"

    if "gzip" == bundleExt.split('/')[1]:
        bundle.extractDatasAsTar(bundleId, bundleBin)
    elif "zip" == bundleExt.split('/')[1]:
        bundle.extractDatasAsZip(bundleId, bundleBin)
    sharedBundleDatas["status"] = "end extraction"

    sharedBundleDatas["status"] = "start analyze"
    analyzedBundle = None
    analyzedBundle = bundle.analyze()
    sharedBundleDatas["status"] = "end analyze"
    sharedBundleDatas["datas"] = analyzedBundle

    deleteUnusedFiles(bundle, sharedBundleDatas)

def deleteUnusedFiles(bundle, sharedBundleDatas):
    sharedBundleDatas["status"] = 'delete ' + "tmp/" + bundle.id + ".tar.gz"
    os.remove("tmp/" + bundle.id + ".tar.gz")
    shutil.rmtree("tmp/" + bundle.id)

class Bundle:
    def __init__(self, bundleId):
        self.id = bundleId
        self.path = None

    def extractDatasAsTar(self, bundleId, datas):
        '''
        Extract bundle as a tar file.
        '''
        tempFilePath = "tmp/" + bundleId + ".tar.gz"

        self.path = "tmp/" + str(bundleId)

        f = open(tempFilePath, 'w')
        f.write(datas)
        f.close()

        tar = tarfile.open(tempFilePath, "r")
        tar.extractall(self.path)

        tar.close()


    def extractDatasAsZip(self, bundleId, datas):
        '''
        Extract bundle as a zip file.
        '''
        tempFilePath = "tmp/" + bundleId + ".zip"
        self.path = "tmp/" + str(bundleId)
        f = open(tempFilePath, 'w')
        f.write(datas)
        f.close()
        
        # TODO : extract datas

    def analyze(self):
        '''
        Analyze the bundle an return a description for each plugin.
        '''
        p = plugin.Plugin()
        pluginCache = tuttle.core().getPluginCache()
        pluginCache.addDirectoryToPath(self.path)
        tuttle.core().preload(False)
        plugins = pluginCache.getPlugins()

        pluginsDescription = {'plugins':[], 'total': len(plugins)}

        for currentPlugin in plugins:
            pluginsDescription['plugins'].append(p.getPluginProperties(currentPlugin))

        return pluginsDescription
