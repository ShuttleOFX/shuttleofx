from pyTuttle import tuttle
import logging, time, ConfigParser

configParser =  ConfigParser.RawConfigParser()
configParser.read('configuration.cfg')

class RenderScene:
    def __init__(self):
        self.nodes = []
        self.tuttleGraph = tuttle.Graph()
        self.globalOfxPluginPath = configParser.get("OFX_PATH", "globalOfxPluginPath")
        self.graph = None
        self.status = 0 #-1 aborted 0 undefined, 1 loading, 2 computing  3, complete


    def setPluginPaths(self, ofxPluginPath):

        tuttle.core().getPluginCache().addDirectoryToPath(self.globalOfxPluginPath)
        tuttle.core().getPluginCache().addDirectoryToPath(ofxPluginPath)
        pluginCache = tuttle.core().getPluginCache()
        tuttle.core().preload(False)


    def loadGraph(self, graphToLoad, outputFilename):
        self.graph = graphToLoad
        self.status = 1
        try:
            for node in graphToLoad['scene']['nodes']:
                tuttleNode = self.tuttleGraph.createNode(str(node['plugin']))
                for parameter in node['parameters']:
                    param = tuttleNode.getParam(str(parameter["id"]))

                    if type(parameter["value"]) == unicode:
                        parameter["value"] = str(parameter["value"])

                    param.setValue(parameter["value"])
                self.nodes.append(tuttleNode)

            for connection in graphToLoad['scene']['connections']:
                 self.tuttleGraph.connect( [ self.nodes[connection['src']['id']],  self.nodes[connection['dst']['id']]] )

            outputFilenameParameter = self.nodes[len(self.nodes)-1].getParam("filename")
            outputFilenameParameter.setValue( outputFilename )

        except Exception as e:
            logging.error("error in the graph " + str(e))

    def computeGraph(self):
        try:
            self.status = 2
            self.graph["startDate"] = time.time()
            self.tuttleGraph.compute(self.nodes[len(self.nodes)-1] )
            self.status = 3
        except Exception as e:
            self.status = -1
            logging.error("Error in render: " + str(e))

    def getStatus(self):
        return self.status