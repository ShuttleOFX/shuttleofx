from pyTuttle import tuttle
import logging

propTypeToPythonType = {
    tuttle.ePropTypeDouble: float,
    tuttle.ePropTypeInt: int,
    tuttle.ePropTypeNone: None,
    tuttle.ePropTypePointer: str,
    tuttle.ePropTypeString: str,
}

class Plugin:
    def __init__(self):
        self.rawIdentifier = None
        self.name = None
        self.version = {}
        self.clips = []
        self.parameters = []
        self.properties = []


    def getDictOfProperty(self, prop):

        pythonType = propTypeToPythonType[prop.getType()]

        return {
            "name": prop.getName(),
            "readOnly": prop.getPluginReadOnly(),
            "type": prop.getType(),
            "modifiedBy": prop.getModifiedBy(),
            "value": [pythonType(v) for v in prop.getStringValue().split(', ')]
        }

    def getDictOfProperties(self, props):
        properties = []
        for p in props:
            properties.append(self.getDictOfProperty(p))
        return properties

    def getPluginProperties(self, pluginToAnalyse):
        logging.info('Analysing plugin for ' + str(pluginToAnalyse.getRawIdentifier()))

        self.uri = "/plugins/" + str(pluginToAnalyse.getIdentifier())
        self.rawIdentifier = str(pluginToAnalyse.getIdentifier())
        self.version = {
            'major': pluginToAnalyse.getVersionMajor(),
            'minor': pluginToAnalyse.getVersionMinor()
        }
        
        try:
            node = tuttle.createNode(pluginToAnalyse.getIdentifier())
        except Exception as e:
            logging.error("Error in node creation: " + str(e))
            return (self.__dict__)

        # plugin properties
        self.properties = self.getDictOfProperties(node.getProperties())

        # list all properties on parameters of the node
        params = []
        for parameters in node.getParamSet().getParams():
            params.append(self.getDictOfProperties(parameters.getProperties()))
        self.parameters = params

        # list all properties on Clips
        clips = []
        for clip in node.getClipImageSet().getClips():
            clips.append(self.getDictOfProperties(clip.getProperties()))
        self.clips = clips

        return (self.__dict__)
