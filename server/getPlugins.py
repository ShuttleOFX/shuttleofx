#!/usr/bin/python
from flask import Flask, jsonify
from pyTuttle import tuttle
from ofxPlugins import analyze
import ConfigParser, requests, json


app = Flask(__name__, static_folder='', static_url_path='')

configParser =  ConfigParser.RawConfigParser()
configParser.read('ofxPlugins/configuration.conf')

version = "0.0.1"

globalOfxPluginPath = configParser.get("OFX_PATH", "globalOfxPluginPath")
tuttle.core().getPluginCache().addDirectoryToPath(globalOfxPluginPath)

tuttle.core().preload(False)
pluginCache = tuttle.core().getPluginCache()
plugins = pluginCache.getPlugins()


@app.route('/plugins', methods=['GET'])
def getPlugins():
    pluginsDescription = {'plugins':[], 'total': 0}
    for plugin in plugins:
        pluginsDescription['plugins'].append(analyze.getPluginProperties(plugin))
    # json_data= open('plugins.json')
    # data = json.load(json_data)
    # json_data.close()

    headers = {
        'content-type': 'application/json'
    }

    # return jsonify(**data)
    return jsonify(**pluginsDescription)


@app.route('/plugins/<string:pluginId>', methods=['GET'])
def getPlugin(pluginId):
    plugin = pluginCache.getPluginById(str(pluginId))
    pluginDescription = analyze.getPluginProperties(plugin)
    return jsonify(**pluginDescription)

    # json_data= open('plugin.json')
    # data = json.load(json_data)
    # json_data.close()
    # return jsonify(**data)



if __name__ == '__main__':
    app.run(host=configParser.get("APP_PLUGIN", "host"), port=configParser.getint("APP_PLUGIN", "port"), debug=True)
