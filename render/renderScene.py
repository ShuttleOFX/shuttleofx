from pyTuttle import tuttle
import logging
import time
import ConfigParser

configParser =  ConfigParser.RawConfigParser()
configParser.read('render.cfg')

globalOfxPluginPath = configParser.get("OFX_PATH", "globalOfxPluginPath")


class ProgressHandle(tuttle.IProgressHandle):
    def __init__(self, renderSharedInfo):
        super(ProgressHandle, self).__init__()
        self.renderSharedInfo = renderSharedInfo

    def beginSequence(self):
        """Called before the beginning of the process
        """
        print "---> beginSequence"

    def setupAtTime(self):
        """Called when setting up an image
        """
        pass

    def processAtTime(self):
        """Called before processing an image
        """
        self.renderSharedInfo["status"] = 99
        print "---> processAtTime"

    def endSequence(self):
        """Called at the end of the process
        """
        print "---> endSequence"

def setPluginPaths(ofxPluginPath):
    tuttle.core().getPluginCache().addDirectoryToPath(ofxPluginPath)
    pluginCache = tuttle.core().getPluginCache()
    tuttle.core().preload(False)

def loadGraph(scene, outputFilename):
    tuttleGraph = tuttle.Graph()
    status = 1
    try:
        nodes = []
        for node in scene['nodes']:
            tuttleNode = tuttleGraph.createNode(str(node['plugin']))
            for parameter in node['parameters']:
                param = tuttleNode.getParam(str(parameter["id"]))

                if type(parameter["value"]) == unicode:
                    parameter["value"] = str(parameter["value"])

                param.setValue(parameter["value"])
            nodes.append(tuttleNode)

        for connection in scene['connections']:
            # TODO: replace src/dst with from/to.
            tuttleGraph.connect([
                nodes[connection['src']['id']],
                nodes[connection['dst']['id']],
                ])

        # TODO: what is the right way to retrieve the output node.
        outputNode = nodes[-1]
        # TODO:
        # if outputNode.getProperties().getProperty("OfxPropContextWriter").getValue():
        outputFilenameParameter = outputNode.getParam("filename")
        outputFilenameParameter.setValue( outputFilename )

        return tuttleGraph

    except Exception as e:
        logging.error("error in the graph " + str(e))


def computeGraph(renderSharedInfo, newRender, outputFilename):
    print "computeGraph"
    
    try:
        renderSharedInfo['startDate'] = time.time()

        #TODO set the right plugin path
        setPluginPaths(globalOfxPluginPath)

        renderSharedInfo['status'] = 1
        tuttleGraph = loadGraph(newRender['scene'], outputFilename)

        renderSharedInfo['status'] = 2

        computeOptions = tuttle.ComputeOptions()
        computeOptions.setVerboseLevel(tuttle.eVerboseLevelError)
        ## Create handle and set it in ComputeOptions
        progressHandle = ProgressHandle(renderSharedInfo)
        computeOptions.setProgressHandle(progressHandle)

        tuttleGraph.compute(computeOptions)

        renderSharedInfo['status'] = 3

    except Exception as e:
        renderSharedInfo['status'] = -1
        logging.error("Error in render: " + str(e))
