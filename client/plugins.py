from flask import Flask, request, jsonify
from flask import render_template, jsonify, json

import ConfigParser, requests

from client import app


def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string


configParser =  ConfigParser.RawConfigParser()
configParser.read('client/configuration.conf')
version = "0.0.1"

analyzeRootUri = configParser.get("APP_CLIENT", "analyzeRootUri")



@app.route('/plugins', methods=['GET', 'POST'])
def getPlugins(pluginName=None):
    resp = requests.get(analyzeRootUri+"/plugins")
    # resp = requests.get("http://localhost:5004/plugins/")

    return render_template('plugins.html', dico=resp.json())


@app.route('/plugins/<pluginId>', methods=['GET'])
def getPlugin(pluginId):
    resp = requests.get(analyzeRootUri+"/plugins/"+pluginId)
    # resp = requests.get("http://localhost:5004/plugins/<pluginId>")

    return render_template('plugin.html', dico=resp.json())



# @app.route('/pluginsWrong')
# def getPluginsWrong(pluginName=None):
#     return render_template('plugins.html', dico=dico)


# @app.route('/pluginsWrong/<pluginName>')
# def pluginWrong(pluginName=None):
#     newdico = dict(dico)
#     newdico["currentPlugin"] = pluginName
#     return render_template('plugin.html', dico=newdico)


if __name__ == "__main__":
    app.run(host=configParser.get("APP_CLIENT", "host"), port=configParser.getint("APP_CLIENT", "port"), debug=True)
