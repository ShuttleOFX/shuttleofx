from pyTuttle import tuttle
import logging

propTypeToPythonType = {
    tuttle.ePropTypeDouble: float,
    tuttle.ePropTypeInt: int,
    tuttle.ePropTypeNone: None,
    tuttle.ePropTypePointer: str,
    tuttle.ePropTypeString: str,
}

class Plugin(object):
    def __init__(self, tuttlePlugin):
        self.rawIdentifier = None
        self.label = None
        self.version = {}
        self.clips = []
        self.parameters = []
        self.properties = {}
        self.initFromPlugin(tuttlePlugin)

    def convertTuttlePropertyToDict(self, prop):

        pythonType = propTypeToPythonType[prop.getType()]

        # Convert SWIG binding list in python
        valuesCPP = prop.getValues()
        values = []
        if prop.getType() != tuttle.ePropTypePointer and prop.getType() != tuttle.ePropTypeNone:
            values = [valuesCPP[i] for i in range(valuesCPP.size())]

        value = values[0] if values else None

        return {
            "readOnly": prop.getPluginReadOnly(),
            "type": prop.getType(),
            "modifiedBy": prop.getModifiedBy(),
            "value": value,  # TODO: rename propValue
            "propValues": values,
        }

    def convertTuttlePropertiesToDict(self, tuttleProperties):
        properties = {}
        for tuttleProperty in tuttleProperties:
            prop = self.convertTuttlePropertyToDict(tuttleProperty)
            properties[tuttleProperty.getName()] = prop
        return properties

    def initFromPlugin(self, tuttlePlugin):
        logging.info('Analysing plugin for ' + str(tuttlePlugin.getRawIdentifier()))
        self.rawIdentifier = str(tuttlePlugin.getIdentifier())
        self.version = {
            'major': tuttlePlugin.getVersionMajor(),
            'minor': tuttlePlugin.getVersionMinor()
        }

        try:
            node = tuttle.createNode(tuttlePlugin.getIdentifier())
        except Exception as e:
            logging.error("Error in node creation: " + str(e))
            return

        # plugin properties
        self.properties = self.convertTuttlePropertiesToDict(node.getProperties())

        # list all properties on parameters of the node
        params = []
        for parameters in node.getParamSet().getParams():
            params.append(self.convertTuttlePropertiesToDict(parameters.getProperties()))
        self.parameters = params

        # list all properties on Clips
        clips = []
        for clip in node.getClipImageSet().getClips():
            clips.append(self.convertTuttlePropertiesToDict(clip.getProperties()))
        self.clips = clips
