#!/usr/bin/python
from flask import Flask, request, jsonify, send_file
import os
import uuid
import tempfile
import ConfigParser

import renderScene

configParser =  ConfigParser.RawConfigParser()
configParser.read('configuration.cfg')

app = Flask(__name__, static_folder='', static_url_path='')

renders = []
listImg = {}

currentAppDir = os.path.dirname(__file__)
tmpRenderingPath = os.path.join(currentAppDir, "render")
if not os.path.exists(tmpRenderingPath):
  os.mkdir(tmpRenderingPath)


# send graph informations, nodes and connections
@app.route('/render', methods=['POST'])
def newRender():
    r = renderScene.RenderScene()

    datas = request.json
    userID = "johnDoe"
    renderID = str(uuid.uuid1())

    tmpFile = tempfile.mkstemp(prefix='tuttle_', suffix="_" + userID + ".png", dir=tmpRenderingPath)
    resourcePath = os.path.basename(tmpFile[1])

    newRender = {}
    newRender['id'] = renderID
    newRender['outputFile'] = resourcePath
    newRender['scene'] = datas

    app.logger.debug("new resource is " + resourcePath)
    renders.append( newRender )

    r = renderScene.RenderScene()
    
    r.setPluginPaths("")
    r.loadGraph(newRender, outputFilename=tmpFile[1])
    r.computeGraph()
    
    return jsonify(render=newRender)


@app.route('/render/<renderID>', methods=['PUT'])
def updateRequest(renderPath):
    for render in renders:
        if renderID not in render:
            app.logger.error('id '+renderID+" doesn't exists")
            abort(404)
    for key, value in request.json["update"].items():
        renders[renderID][key] = value

# return compute status
@app.route('/stats/', methods=['GET'])
def getStatus():
    global r
    return str(r.getStatus())


# return all renders in json format
@app.route('/render', methods=['GET'])
def getRenders():
    totalRenders = {"renders": renders}
    return jsonify(**totalRenders)


# get a render by id in json format
@app.route('/render/<renderID>', methods=['GET'])
def getRenderById(renderID):
    global renders

    for render in renders:
        if renderID == render['id']:
            return jsonify(render=render)
    jsonify(render=None)
    app.logger.error('id '+ renderID +" doesn't exists")
    abort(404)


@app.route('/render/<renderId>/resources/<resourceId>', methods=['GET'])
def resource(renderId, resourceId):
    if os.path.isfile(tmpRenderingPath + "/" + resourceId):
        return send_file( tmpRenderingPath + "/" + resourceId )
    else:
        logging.error(tmpRenderingPath + resourceId + " doesn't exists")
        abort(404)


# delete a render from the render array
@app.route('/render/<renderID>', methods=['DELETE'])
def deleteRenderById(renderID):
    if renderID not in renders:
        app.logger.error('id '+renderID+" doesn't exists")
        abort(400)
    del renders[renderID]


@app.route('/resources/', methods=['POST'])
def addResource():
    global listImg

    uid = str(uuid.uuid1())
    img = request.data
    print request.headers
    ext = request.headers.get("Content-Type").split('/')[1]

    imgFile = "/resources/" + uid + "." + ext

    f = open("../resources/" + uid + "." + ext, 'w')
    f.write(img)
    f.close()

    objectId = {'id': uid,
                'uri': imgFile
    }

    listImg[uid] = imgFile

    return jsonify(**objectId)

@app.route('/resources/<resourceId>', methods=['GET'])
def getResource(resourceId):
    if os.path.isfile("../resources/" + resourceId):
        return send_file("../resources/" + resourceId)
    abort(404)
    return

@app.route('/resources/', methods=['GET'])
def getResourcesDict():
    global listImg
    ret = {"files" : listImg }
    return jsonify(**ret)

def getAllResources():
    for image in os.listdir("../resources"):
        _id = str(uuid.uuid4())
        listImg[_id] = "/resources/" + str(image)

if __name__ == "__main__":
	app.run(host=configParser.get("APP_RENDER", "host"), port=configParser.getint("APP_RENDER", "port"), debug=True)