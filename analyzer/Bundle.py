import os
import shutil
import tarfile
import threading
import multiprocessing
from multiprocessing import Process


from pyTuttle import tuttle
import analyzePlugin

class Bundle:
    def __init__(self, bundleId):
        self.id = bundleId
        self.path = None

    def extractDatasAsTar(self, bundleId, datas):
        tempFilePath = "tmp/" + bundleId + ".tar.gz"

        self.path = "tmp/" + str(bundleId)
        f = open(tempFilePath, 'w')
        f.write(datas)
        f.close()

        tar = tarfile.open(tempFilePath, "r")
        tar.extractall(self.path)
        

        tar.close()
        os.remove(tempFilePath)

    def extractDatasAsZip(self, bundleId, datas):
        tempFilePath = "tmp/" + bundleId + ".zip"

        self.path = "tmp/" + str(bundleId)
        f = open(tempFilePath, 'w')
        f.write(datas)
        f.close()
        
        # TODO

        os.remove(tempFilePath)

    def asyncAnalyze(self, queue):
        pluginCache = tuttle.core().getPluginCache()
        pluginCache.addDirectoryToPath(self.path)
        tuttle.core().preload(False)
        plugins = pluginCache.getPlugins()

        pluginsDescription = {'plugins':[], 'total': len(plugins)}

        for plugin in plugins:
            pluginsDescription['plugins'].append(analyzePlugin.getPluginProperties(plugin)

        queue.put(pluginsDescription)

    def analyze(self):
        result_queue = multiprocessing.Queue()

        process = Process(target=self.asyncAnalyze, args=(result_queue,))
        process.start()
        analyzedBundle = result_queue.get()
        process.join()

        shutil.rmtree(self.path)

        return analyzedBundle