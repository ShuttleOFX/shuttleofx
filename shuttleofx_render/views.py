
import os
import uuid
import json
import atexit
import logging
import tempfile
import multiprocessing

from flask import request, jsonify, send_file, abort, Response, make_response
from bson import json_util, ObjectId

import config
import renderScene

# list of all computing renders
g_renders = {}
g_rendersSharedInfo = {}

# Pool for rendering jobs
# processes=None => os.cpu_count()
g_pool = multiprocessing.Pool(processes=4)
g_enablePool = False

# Manager to share rendering information
g_manager = multiprocessing.Manager()

def mongodoc_jsonify(*args, **kwargs):
    return Response(json.dumps(args[0], default=json_util.default), mimetype='application/json')

def remapPath(datas):
    '''
    Replace PATTERNS with real filepaths.
    '''
    outputResources = []
    for node in datas['nodes']:
        for parameter in node['parameters']:
            logging.warning('param: %s %s', parameter['id'], parameter['value'])
            if isinstance(parameter['value'], (str, unicode)):

                if '{RESOURCES_DIR}' in parameter['value']:
                    parameter['value'] = parameter['value'].replace('{RESOURCES_DIR}', config.resourcesPath)

                if '{UNIQUE_OUTPUT_FILE}' in parameter['value']:
                    prefix, suffix = parameter['value'].split('{UNIQUE_OUTPUT_FILE}')
                    _, tmpFilepath = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=config.renderDirectory)
                    outputResources.append(os.path.basename(tmpFilepath))
                    parameter['value'] = tmpFilepath

    return outputResources


@config.g_app.route('/')
def index():
    return "ShuttleOFX Render service"

@config.g_app.route('/render', methods=['POST'])
def newRender():
    '''
    Create a new render and return graph information.
    '''

    datas = request.json
    renderID = str(uuid.uuid1())
    logging.info("RENDERID: " + renderID)
    outputResources = remapPath(datas)

    newRender = {}
    newRender['id'] = renderID
    # TODO: return a list of output resources in case of several writers.
    newRender['outputFilename'] = outputResources[0]
    newRender['scene'] = datas
    g_renders[renderID] = newRender

    config.g_app.logger.debug('new resource is ' + newRender['outputFilename'])

    renderSharedInfo = g_manager.dict()
    renderSharedInfo['status'] = 0
    g_rendersSharedInfo[renderID] = renderSharedInfo

    if g_enablePool:
        g_pool.apply(renderScene.launchComputeGraph, args=[renderSharedInfo, newRender])
    else:
        renderScene.launchComputeGraph(renderSharedInfo, newRender)

    return jsonify(render=newRender)


@config.g_app.route('/progress/<renderID>', methods=['GET'])
def getProgress(renderID):
    '''
    Return render progress.
    '''
    return str(g_rendersSharedInfo[renderID]['status'])


@config.g_app.route('/render', methods=['GET'])
def getRenders():
    '''
        Returns all renders in JSON format
    '''
    totalRenders = {"renders": g_rendersSharedInfo}
    return jsonify(**totalRenders)


@config.g_app.route('/render/<renderID>', methods=['GET'])
def getRenderById(renderID):
    '''
    Get a render by id in json format.
    '''

    for key, render in g_renders.iteritems():
        if renderID == key:
            return jsonify(render=render)
    logging.error('id '+ renderID +" doesn't exists")
    abort(make_response("id "+ renderID +" doesn't exists", 404))


@config.g_app.route('/render/<renderId>/resource/<resourceId>', methods=['GET'])
def resource(renderId, resourceId):
    '''
    Returns file resource by renderId and resourceId.
    '''
    if not os.path.isfile( os.path.join(config.renderDirectory, resourceId) ):
        logging.error(config.renderDirectory + resourceId + " doesn't exists")
        abort(make_response(config.renderDirectory + resourceId + " doesn't exists", 404))

    return send_file( os.path.join(config.renderDirectory, resourceId) )

@config.g_app.route('/render/<renderID>', methods=['DELETE'])
def deleteRenderById(renderID):
    '''
    Delete a render from the render array.
    TODO: needed?
    TODO: kill the corresponding process?
    '''
    if renderID not in g_renders:
        logging.error("id "+renderID+" doesn't exists")
        abort(make_response("id "+renderID+" doesn't exists", 404))
    del g_renders[renderID]


@config.g_app.route('/resource', methods=['POST'])
def addResource():
    '''
    Upload resource file on the database
    '''
    if not 'file' in request.files:
        abort(make_response("Empty request", 500))

    mimetype = request.files['file'].content_type

    if not mimetype:
        logging.error("Invalid resource.")
        abort(make_response("Invalid resource.", 404))

    uid = config.resourceTable.insert({
        "mimetype" : mimetype,
        "size" : request.content_length,
        "name" : request.files['file'].filename})

    imgFile = os.path.join(config.resourcesPath, str(uid))
    file = request.files['file']
    file.save(imgFile)

    resource = config.resourceTable.find_one({ "_id" : ObjectId(uid)})
    return mongodoc_jsonify(resource)


@config.g_app.route('/resource/<resourceId>', methods=['GET'])
def getResource(resourceId):
    '''
    Returns resource file.
    '''
    resource = os.path.join(config.resourcesPath, resourceId)

    if os.path.isfile(resource):
        return send_file(resource)
    else:
        logging.error("can't find " + resource)
        abort(make_response("can't find " + resource, 404))

@config.g_app.route('/resource/', methods=['GET'])
def getResourcesDict():
    '''
    Returns all resources files from db.
    '''
    count = int(request.args.get('count', 10))
    skip = int(request.args.get('skip', 0))
    resources = config.resourceTable.find().limit(count).skip(skip)
    return mongodoc_jsonify({"resources":[ result for result in resources ]})

@config.g_app.route('/upload', methods=['GET'])
def uploadPage():
    return """<!DOCTYPE html>
      <html lang="en">
      <head>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h3 class="text-muted">UPLOAD A RESOURCE</h3>
          </div>
          <hr/>
          <div>
            <form action="/resource" method="POST" enctype="multipart/form-data">
              <input type="file" name="file">
              <br/><br/>
              <input type="submit" value="Upload">
            </form>
          </div>
        </div>
      </body>
      </html>"""

@atexit.register
def cleanPool():
    '''
    Close processes and quit pool at exit.
    '''
    g_pool.close()
    g_pool.terminate()
    g_pool.join()

if __name__ == '__main__':
    config.g_app.run(host="0.0.0.0",port=5005,debug=True)
