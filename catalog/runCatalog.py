
import os
import json
import pymongo
import ConfigParser

from bson import json_util
from flask import Flask, jsonify, Response, request, abort

from Bundle import Bundle
from Plugin import Plugin

app = Flask(__name__)

currentDir = os.path.dirname(os.path.realpath(__file__))

config = ConfigParser.ConfigParser()
config.read('catalog.cfg')

client = pymongo.MongoClient(config.get('MONGODB', 'hostname'), config.getint('MONGODB', 'port'))
db = client.__getattr__(config.get('MONGODB', 'dbName'))
bundleTable = db.__getattr__(config.get('MONGODB', 'bundleTable'))
pluginTable = db.__getattr__(config.get('MONGODB', 'pluginTable'))


@app.route("/")
def index():
    return "test catalog with mongodb"


def mongodoc_jsonify(*args, **kwargs):
    return Response(json.dumps(args[0], default=json_util.default), mimetype='application/json')

@app.route("/bundle", methods=["POST"])
def newBundle():
    bundleId = request.get_json().get('bundleId', None)
    bundleName = request.get_json().get('name', None)

    if bundleId == None or bundleName == None:
        abort(404)

    bundle = Bundle(bundleId, bundleName)
    
    bundleTable.insert(bundle.__dict__)

    requestResult = bundleTable.find_one({"bundleId": bundleId})
    return mongodoc_jsonify(requestResult)

@app.route('/bundle/<bundleId>/archive', methods=['POST'])
def uploadArchive(bundleId):
    requestResult = bundleTable.find_one({"bundleId": bundleId})
    if requestResult == None:
        abort(404)

    return mongodoc_jsonify(requestResult)

@app.route("/bundle")
def getBundles():
    count = int(request.args.get('count', 10))
    skip = int(request.args.get('skip', 0))
    requestResult = bundleTable.find().limit(count).skip(skip)
    return mongodoc_jsonify({"bundles":[ result for result in requestResult ]})

@app.route("/bundle/<int:bundleId>")
def getBundle(bundleId):
    requestResult = bundleTable.find_one({"bundleId": bundleId})
    if requestResult == None:
        abort(404)

    return mongodoc_jsonify(requestResult)


@app.route("/bundle/<int:bundleId>", methods=["DELETE"])
def deleteBundle(bundleId):
    requestResult = bundleTable.find_one({"bundleId": bundleId})
    if requestResult == None:
        abort(404)

    for plugin in requestResult.plugins:
        deleteStatus = pluginTable.remove({"pluginId":pluginId})
        if deleteStatus['n'] == 0:
            abort(404)

    deleteStatus = bundleTable.remove({"bundleId":bundleId})

    if deleteStatus['n'] == 0:
        abort(404)

    return jsonify(**deleteStatus)

@app.route("/bundle/<int:bundleId>/plugin", methods=['POST'])
def newPlugin(bundleId):
    pluginId = request.get_json().get('pluginId', None)
    pluginName = request.get_json().get('name', None)

    if pluginId == None or pluginName == None:
        abort(404)

    plugin = Plugin(pluginId, bundleId, pluginName)
    
    pluginTable.insert(plugin.__dict__)

    requestResult = pluginTable.find_one({"pluginId": pluginId})
    return mongodoc_jsonify(requestResult)


@app.route("/bundle/<int:bundleId>/plugin")
def getPlugins(bundleId):
    count = int(request.args.get('count', 10))
    skip = int(request.args.get('skip', 0))
    requestResult = pluginTable.find({"bundleId":bundleId}).limit(count).skip(skip)
    return mongodoc_jsonify({"plugins":[ result for result in requestResult ]})

@app.route("/plugin")
def getAllPlugins():
    count = int(request.args.get('count', 10))
    skip = int(request.args.get('skip', 0))
    requestResult = pluginTable.find().limit(count).skip(skip)
    return mongodoc_jsonify({"plugins":[ result for result in requestResult ]})

@app.route("/bundle/<int:bundleId>/plugin/<pluginId>")
@app.route("/plugin/<pluginId>")
def getPlugin(bundleId):
    requestResult = pluginTable.find_one({"pluginId": pluginId})
    if requestResult == None:
        abort(404)

    return mongodoc_jsonify(requestResult)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002 ,debug=True)

