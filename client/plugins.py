from flask import Flask, request, jsonify
from flask import render_template, jsonify, json

import ConfigParser
import requests

from client import app




def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string


configParser =  ConfigParser.RawConfigParser()
configParser.read('client/configuration.conf')
version = "0.0.1"

analyzeRootUri = configParser.get("APP_CLIENT", "analyzeRootUri")
catalogRootUri = configParser.get("APP_CLIENT", "catalogRootUri")




@app.route('/plugins', methods=['GET'])
def getPlugins(pluginName=None):

    resp = requests.get(catalogRootUri+"/plugins", params=request.args)

    return render_template('plugins.html', dico=resp.json())


@app.route('/plugins/<pluginId>', methods=['GET'])
def getPlugin(pluginId):
    resp = requests.get(analyzeRootUri+"/plugins/"+pluginId)
    print resp.text
    return render_template('plugin.html', plugin=resp.json())






