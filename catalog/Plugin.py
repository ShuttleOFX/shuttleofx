

class Plugin(object):
    def __init__(self, pluginId, bundleId, pluginName=""):
        self.pluginId = pluginId
        self.bundleId = bundleId
        self.name = pluginName
        self.shortName = None
        self.description = ""
        self.shortDescription = ""
        self.version = [0, 0]
        self.details = None
        self.tags = []
        self.presets = None
        self.rate = 0
        self.defautImagePath = None
        self.sampleImagesPath = []
        self.parameters = []
        self.properties = []
        self.clip = []
        self.uri= None
        self.rawIdentifier = None

    def setDescription(self, description):
        self.description = description

    def addPluginDetails(self, details):
        self.details = details

    def setRating(self, val):
        self.rate = val

    def getRating(self):
        return self.rate

    def addSampleImages(self, paths):
        if isinstance(paths, str):
            self.sampleImagesPath.append(paths)

        if isinstance(paths, list):
            for path in paths:
                self.sampleImagesPath.append(path)

    def printBundle(self):
        print "Plugin :"
        print "pluginId:", self.pluginId
        print "bundleId:", self.bundleId
        print "description:", self.description
        print "shortDescription:", self.shortDescription
        print "version:", self.version
        print "details:", self.details
        print "tags:", self.tags
        print "presets:", self.presets
        print "rate:", self.rate
        print "defautImagePath:", self.defautImagePath
        print "sampleImagesPath:", self.sampleImagesPath
