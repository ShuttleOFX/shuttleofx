#!/usr/bin/env python
from flask import Flask, request, jsonify, send_file, abort, Response
import os
import uuid
import atexit
import logging
import tempfile
import ConfigParser
import multiprocessing

import renderScene

configParser =  ConfigParser.RawConfigParser()
configParser.read('render.cfg')

g_app = Flask(__name__, static_folder='', static_url_path='')

# list of all computing renders
g_renders = {}
g_rendersSharedInfo = {}

# Pool for rendering jobs
# processes=None => os.cpu_count()
g_pool = multiprocessing.Pool(processes=4)
g_enablePool = False

# Manager to share rendering information
g_manager = multiprocessing.Manager()

# list of all rendered resources
g_listImg = {}

currentAppDir = os.path.dirname(os.path.abspath(__file__))

renderDirectory = os.path.join(currentAppDir, configParser.get('RENDERED_FILES', 'renderedFilesDirectory'))
if not os.path.exists(renderDirectory):
    os.makedirs(renderDirectory)

resourcesPath = os.path.join(currentAppDir, configParser.get('RESOURCES', 'resourcesDirectory'))
if not os.path.exists(resourcesPath):
    os.makedirs(resourcesPath)


# TODO: replace multiprocessing with https://github.com/celery/billiard to have timeouts in the Pool.

# TODO atexit:
# g_pool.terminate()
# g_pool.join()

def remapPath(datas):
    '''
    Replace PATTERNS with real filepaths.
    '''
    outputResources = []
    for node in datas['nodes']:
        for parameter in node['parameters']:
            logging.info('param:', parameter['id'], parameter['value'])
            if isinstance(parameter['value'], (str, unicode)):

                if '{RESOURCES_DIR}' in parameter['value']:
                    parameter['value'] = parameter['value'].replace('{RESOURCES_DIR}', resourcesPath)

                if '{UNIQUE_OUTPUT_FILE}' in parameter['value']:
                    prefix, suffix = parameter['value'].split('{UNIQUE_OUTPUT_FILE}')
                    _, tmpFilepath = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=renderDirectory)
                    outputResources.append(os.path.basename(tmpFilepath))
                    parameter['value'] = tmpFilepath

    return outputResources


@g_app.route('/render', methods=['POST'])
def newRender():
    '''
    Create a new render and return graph informations.
    '''
    global g_app, g_renders, g_pool

    datas = request.json
    renderID = str(uuid.uuid1())

    outputResources = remapPath(datas)

    newRender = {}
    newRender['id'] = renderID
    # TODO: return a list of output resources in case of several writers.
    newRender['outputFilename'] = outputResources[0]
    newRender['scene'] = datas
    g_renders[renderID] = newRender

    g_app.logger.debug('new resource is ' + newRender['outputFilename'])

    renderSharedInfo = g_manager.dict()
    renderSharedInfo['status'] = 0
    g_rendersSharedInfo[renderID] = renderSharedInfo

    if g_enablePool:
        g_pool.apply(renderScene.computeGraph, args=[renderSharedInfo, newRender])
    else:
        renderScene.computeGraph(renderSharedInfo, newRender)
    
    return jsonify(render=newRender)


@g_app.route('/progress/<renderID>', methods=['GET'])
def getProgress(renderID):
    '''
    Return render progress.
    '''
    global g_rendersSharedInfo
    return str(g_rendersSharedInfo[renderID]['status'])


@g_app.route('/render', methods=['GET'])
def getRenders():
    '''
        Returns all renders in JSON format
    '''
    totalRenders = {"renders": g_rendersSharedInfo}
    return jsonify(**totalRenders)


@g_app.route('/render/<renderID>', methods=['GET'])
def getRenderById(renderID):
    '''
    Get a render by id in json format.
    '''
    global g_renders

    for key, render in g_renders.iteritems():
        if renderID == key:
            return jsonify(render=render)
    g_app.logger.error('id '+ renderID +" doesn't exists")
    abort(404)


@g_app.route('/render/<renderId>/resource/<resourceId>', methods=['GET'])
def resource(renderId, resourceId):
    '''
    Returns file resource by renderId and resourceId.
    '''
    if os.path.isfile( os.path.join(renderDirectory, resourceId) ):
        return send_file( os.path.join(renderDirectory, resourceId) )
    else:
        logging.error(renderDirectory + resourceId + " doesn't exists")
        abort(404)


@g_app.route('/render/<renderID>', methods=['DELETE'])
def deleteRenderById(renderID):
    '''
    Delete a render from the render array.
    TODO: needed?
    TODO: kill the corresponding process?
    '''
    if renderID not in g_renders:
        g_app.logger.error('id '+renderID+" doesn't exists")
        abort(400)
    del g_renders[renderID]


@g_app.route('/resources/', methods=['POST'])
def addResource():
    '''
    Upload resource file on the server and returns id and uri.
    '''
    global g_listImg

    uid = str(uuid.uuid1())
    img = request.data
    ext = request.headers.get("Content-Type").split('/')[1]

    imgFile = os.path.join(resourcesPath, uid + '.' + ext)

    f = open(imgFile, 'w')
    f.write(img)
    f.close()

    objectId = {'id': uid,
                'uri': '/resources/' + uid
    }

    g_listImg[uid] = imgFile

    return jsonify(**objectId)


@g_app.route('/resources/<resourceId>', methods=['GET'])
def getResource(resourceId):
    '''
    Returns resource file.
    '''
    global g_listImg

    print json.dumps(g_listImg, indent=4)
    imageName = os.path.basename(g_listImg[resourceId])

    filePath = os.path.join(resourcesPath, imageName)
    if os.path.isfile(filePath):
        return send_file(filePath)
    abort(404)
    return

@g_app.route('/resources/', methods=['GET'])
def getResourcesDict():
    '''
     Returns a list of all resources on server.
    '''
    global g_listImg
    ret = {"files" : g_listImg }
    return jsonify(**ret)

def getAllResources():
    '''
    Fill the list of images with all resources path on the server.
    '''
    global g_listImg
    for image in os.listdir(str(resourcesPath)):
        _id = str(uuid.uuid4())
        g_listImg[_id] = os.path.join(str(resourcesPath), str(image))


@atexit.register
def cleanPool():
    '''
    Close processes and quit pool at exit.
    '''
    global g_pool
    g_pool.close()
    g_pool.terminate()
    g_pool.join()

if __name__ == "__main__":
    getAllResources()
    g_app.run(host=configParser.get("APP_RENDER", "host"), port=configParser.getint("APP_RENDER", "port"), debug=True)
