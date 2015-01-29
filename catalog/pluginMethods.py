from flask import Flask, jsonify, request, abort, send_file

import ConfigParser , psycopg2 , requests , uuid , json , sys
from math import ceil

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func

pathToCommon = "../common"
sys.path.append(pathToCommon)

import models
from models import Plugin, Clip, Property, Parameter

configParser =  ConfigParser.RawConfigParser()
configParser.read('configuration.conf')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://"+configParser.get("DB_CONFIG", "dbUser")+":"+configParser.get("DB_CONFIG", "dbMdp")+"@"+configParser.get("DB_CONFIG", "dbUrl")+"/"+configParser.get("DB_CONFIG", "dbName")

db = SQLAlchemy(app)
@app.route('/plugins', methods=['GET'])
def getAllPlugins() :

    totalPlugins = Plugin.query.count()
    offset = 0
    limPlug = 20
    request.args.get('page', 0)
    request.args.get('size', 20)


    if "size" in request.args:
        limPlug = int(request.args["size"])


    if "page" in request.args:
        offset = limPlug*int(request.args["page"])
        print offset

    retPlugins = {}

    pluginsQuery = Plugin.query.filter(Plugin.pluginId > offset, Plugin.pluginId <= limPlug+offset)
    plugins = Plugin.serialize_list(pluginsQuery)

    if totalPlugins%limPlug !=0 :
        sup = 1
    else : 
        sup = 0

    retPlugins["size"] = limPlug
    retPlugins["page"] = offset
    retPlugins["plugins"] = plugins
    retPlugins["totalPlugin"] = totalPlugins
    retPlugins["pagination"] = int(totalPlugins/limPlug + sup)

    return jsonify(retPlugins)

@app.route("/plugins/<pluginId>", methods=['GET'])
def getThePlugin(pluginId) :
    pl = Plugin.query.filter_by(pluginId=pluginId)
    temp = Plugin.serialize_list(pl)
    plugin = temp[0]

    keyParameters = plugin['parameters']
    keyClip = plugin['clip']
    pluginProperties = plugin['properties']

    del plugin['parameters']
    del plugin['clip']
    del plugin['properties']

    clips = cleanSerializing(keyClip, 'clip', Property)
    parameterProperties = cleanSerializing(keyParameters, 'parameter', Property)
    plugin['properties'] = json.loads(pluginProperties)

    data = {}
    plugin['clips'] = clips
    plugin['parameters'] = parameterProperties
    data['plugin'] = plugin

    return jsonify(**plugin)


def cleanSerializing(myDict, removeParamName, tableObject) : 
    print myDict, removeParamName, tableObject
    newDict = []
    if len(myDict) > 0 :
        for index, key in enumerate(myDict) : 
            if removeParamName == 'clip' :
                print key
                tempVal = tableObject.query.filter_by(clipIdF=key)
            if removeParamName == 'parameter' :
                print key
                tempVal = tableObject.query.filter_by(parameterIdF=key)

            temp = tableObject.serialize_list(tempVal)
            obj = temp[0]
            print obj[removeParamName]
            del obj[removeParamName]
            newDict.append(obj)
    return newDict



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002 ,debug=True)
    db.create_all()

