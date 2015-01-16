#!/usr/bin/python
from flask import Flask, jsonify
from pyTuttle import tuttle
from ofxPlugins import analyze

import logging
import ConfigParser


app = Flask(__name__, static_folder='', static_url_path='')
configParser =  ConfigParser.RawConfigParser()
configParser.read('ofxPlugins/configuration.conf')

version = "0.0.1"

globalOfxPluginPath = configParser.get("OFX_PATH", "globalOfxPluginPath")
tuttle.core().getPluginCache().addDirectoryToPath(globalOfxPluginPath)

tuttle.core().preload(False)
pluginCache = tuttle.core().getPluginCache()
plugins = pluginCache.getPlugins()

@app.route('/', methods=['GET'])
def index():
    index = "<html><head><title>WebOpenFX - Catalog</title></head><body><h1><center>WebOpenFX - Catalog</center></h1><br/><br/><ul><li>version: " + str(version) + "</li></ul></body>"
    return index


@app.route('/plugins/', methods=['GET'])
def getPlugins():
    pluginsDescription = {'plugins':[], 'total': len(plugins)}
    for plugin in plugins:
        pluginsDescription['plugins'].append(analyze.getPluginProperties(plugin))
    return jsonify(**pluginsDescription)

@app.route('/plugins/<string:pluginId>', methods=['GET'])
def getPlugin(pluginId):
    plugin = pluginCache.getPluginById(str(pluginId))
    pluginDescription = analyze.getPluginProperties(plugin)
    return jsonify(**pluginDescription)

if __name__ == '__main__':
    # logging.getLogger().setLevel(10)
    app.run(host=configParser.get("APP_PLUGIN", "host"), port=configParser.getint("APP_PLUGIN", "port"), debug=True)
