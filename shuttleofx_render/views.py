import os
import uuid
import json
import atexit
import logging
import tempfile
import multiprocessing
import mimetypes
import requests
import imghdr
import zipfile
import datetime

from flask import request, jsonify, send_file, abort, Response, make_response
from bson import json_util, ObjectId

import config
import renderScene
import cache

mimetypes.init()
mimetypes.add_type('image/bmp', '.bmp')
mimetypes.add_type('image/x-panasonic-raw', '.raw')

# list of all computing renders
g_renders = {}
g_rendersSharedInfo = {}

# Pool for rendering jobs
# processes=None => os.cpu_count()
g_pool = multiprocessing.Pool(processes=4)
g_enablePool = True

# Manager to share rendering information
g_manager = multiprocessing.Manager()

g_lastClean = datetime.datetime.min

g_tmpLastClean = datetime.datetime.min


def mongodoc_jsonify(*args, **kwargs):
    return Response(json.dumps(args[0], default=json_util.default), mimetype='application/json')


@config.g_app.route('/')
def index():
    return "ShuttleOFX Render service"


@config.g_app.route('/render', methods=['POST'])
def newRender():
    '''
    Create a new render and return graph information.
    '''
    global g_lastClean

    # Clean the cache every interval set in the config
    if g_lastClean < datetime.datetime.now() - datetime.timedelta(hours=config.cleanCacheInterval):
        cache.cleanCache(config.renderDirectory, config.cacheMaxSize)
        # update clean date
        g_lastClean = datetime.datetime.now()

    inputScene = request.json
    logging.warning("inputScene: " + str(inputScene))
    renderID = str(uuid.uuid1())
    logging.info("RENDERID: " + renderID)
    scene, outputResources = renderScene.convertScenePatterns(inputScene)

    newRender = {}
    newRender['id'] = renderID
    # TODO: return a list of output resources in case of several writers.
    newRender['outputFilename'] = outputResources[0]
    newRender['scene'] = scene
    g_renders[renderID] = newRender

    logging.warning('new resource is ' + newRender['outputFilename'])

    renderSharedInfo = g_manager.dict()
    renderSharedInfo['status'] = 0
    g_rendersSharedInfo[renderID] = renderSharedInfo

    # TODO : Generate multiple file paths and test on all files in case of multiple output resources
    filepath = cache.cachePathFromFile(outputResources[0])
    outputFilesExist = os.path.exists(os.path.join(config.renderDirectory, filepath))

    if not outputFilesExist:
        if g_enablePool:
            g_pool.apply(renderScene.launchComputeGraph, args=[renderSharedInfo, newRender])
        else:
            renderScene.launchComputeGraph(renderSharedInfo, newRender)
    else:
        # Already computed, update the file timestamp
        os.utime(os.path.join(config.renderDirectory, filepath), None)
        renderSharedInfo['status'] = 3

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
    logging.error('id ' + renderID + " doesn't exists")
    abort(make_response("id " + renderID + " doesn't exists", 404))


@config.g_app.route('/render/<renderId>/resource/<resourceId>', methods=['GET'])
def resource(renderId, resourceId):
    '''
    Returns file resource by renderId and resourceId.
    '''

    filepath = cache.cachePathFromFile(resourceId)
    if not os.path.isfile(os.path.join(config.renderDirectory, filepath)):
        logging.error(config.renderDirectory + filepath + " doesn't exists")
        abort(make_response(config.renderDirectory + filepath + " doesn't exists", 404))

    return send_file(os.path.join(config.renderDirectory, filepath))


@config.g_app.route('/render/<renderID>', methods=['DELETE'])
def deleteRenderById(renderID):
    '''
    Delete a render from the render array.
    TODO: needed?
    TODO: kill the corresponding process?
    '''
    if renderID not in g_renders:
        logging.error("id " + renderID + " doesn't exists")
        abort(make_response("id " + renderID + " doesn't exists", 404))
    del g_renders[renderID]


def generateProxyThumbnailGraph(folder, fileName):
    '''
    '''

    name, extension = os.path.splitext(fileName)

    graph = {
        u'nodes': [
            {
                u'id': 0,
                u'plugin': u'reader',
                u'parameters': [
                    {u'id': u'filename', u'value': os.path.join(folder, name + extension)}
                ]
            },
            {
                u'id': 1,
                u'plugin': u'tuttle.pngwriter',
                u'parameters': [
                    {u'id': u'filename', u'value': os.path.join(folder, 'proxy', name + '.png')}
                ]
            },
            {
                u'id': 2,
                u'plugin': u'tuttle.resize',
                u'parameters': [
                    {u'id': u'width', u'value': 256},
                    {u'id': u'keepRatio', u'value': 1}
                ]
            },
            {
                u'id': 3,
                u'plugin': u'tuttle.pngwriter',
                u'parameters': [
                    {u'id': u'filename', u'value': os.path.join(folder, 'thumbnail', name + '.png')}
                ]
            }
        ],
        u'connections': [
            {u'src': {u'id': 0}, u'dst': {u'id': 1}},
            {u'src': {u'id': 0}, u'dst': {u'id': 2}},
            {u'src': {u'id': 2}, u'dst': {u'id': 3}},
        ],
        u'options': []
    }

    # return json.dumps(graph)
    return graph


def generateProxies(folder, imgName):
    '''
    Generate png proxy and thumbnail of the input image.
    Input image should is:
     * folder/imgName
    They will be generated in:
     * folder/proxy/imageBaseName.png
     * folder/thumbnail/imageBaseName.png

    :param folder:
    :param imgName:
    :return:
    '''
    renderID = str(uuid.uuid1())
    logging.info("RENDERID: " + renderID)
    scene = generateProxyThumbnailGraph(folder, imgName)
    logging.warning("graph = " + str(scene))

    newRender = {}
    newRender['id'] = renderID
    # TODO: return a list of output resources in case of several writers.
    newRender['scene'] = scene
    g_renders[renderID] = newRender

    # config.g_app.logger.debug('new resource is ' + newRender['outputFilename'])

    renderSharedInfo = g_manager.dict()
    renderSharedInfo['status'] = 0
    g_rendersSharedInfo[renderID] = renderSharedInfo

    if g_enablePool:
        g_pool.apply(renderScene.launchComputeGraph, args=[renderSharedInfo, newRender])
    else:
        renderScene.launchComputeGraph(renderSharedInfo, newRender)

    return jsonify(render=newRender)


def addFile(file):
    '''
    '''

    '''
    if isinstance(file, zipfile.ZipExtFile):
        mimetype = mimetypes.guess_type(file._fileobj.name)
    '''
    mimetype = mimetypes.guess_type(file.filename)

    fileLength = file.content_length

    uid = config.resourceTable.insert({
        "mimetype": mimetype,
        "size": fileLength,
        "name": file.filename,
        "registeredName": ""})

    _, extension = os.path.splitext(file.filename)
    if not extension:
        extension = mimetypes.guess_extension(mimetype)

    imgName = str(uid) + extension
    config.resourceTable.update({"_id": uid}, {"registeredName": imgName})
    imgPath = os.path.join(config.resourcesPath, imgName)

    logging.warning("imgName = " + imgName)
    logging.warning("imgPath = " + imgPath)
    logging.warning("file.filename = " + file.filename)

    file.save(imgPath)
    generateProxies(config.resourcesPath, imgName)

    resource = config.resourceTable.find_one({"_id": ObjectId(uid)})
    return resource


def addArchive_Zipfile(archiveFile):
    '''
    '''
    archive = zipfile.ZipFile(archiveFile, "r")
    resources = []

    for fileName in archive.namelist():
        extractPath = archive.extract(fileName, "/tmp/")

        file = open(extractPath, "rw")
        file.seek(0, os.SEEK_END)
        fileLength = file.tell()
        mimetype, _ = mimetypes.guess_type(extractPath)

        # logging.warning("filename = " + fileName)
        # logging.warning("extractPath = " + extractPath)
        # logging.warning("fileLength = " + fileLength.__str__())
        # logging.warning("mimetype = " + mimetype)

        uid = config.resourceTable.insert({
            "mimetype": mimetype,
            "size": fileLength,
            "name": fileName,
            "registeredName": ""})

        _, extension = os.path.splitext(fileName)
        if not extension:
            extension = mimetypes.guess_extension(mimetype)

        imgName = str(uid) + extension
        config.resourceTable.update({"_id": uid}, {"registeredName": imgName})
        imgPath = os.path.join(config.resourcesPath, imgName)

        imgFile = open(imgPath, "w")
        file.seek(0, 0)
        imgFile.write(file.read(fileLength))
        imgFile.close()

        generateProxies(config.resourcesPath, imgName)

        file.close()
        os.remove(extractPath)


        resource = config.resourceTable.find_one({"_id": ObjectId(uid)})
        resources.append(resource)

    return resources


@config.g_app.route('/resource', methods=['POST'])
def addResource():
    '''
    Upload resource file on the database
    '''
    if not 'file' in request.files:
        abort(make_response("Empty request", 500))

    file = request.files['file']

    mimetype, _ = mimetypes.guess_type(file.filename)
    logging.debug("mimetype = " + mimetype)

    if not mimetype:
        logging.error("Invalid resource.")
        abort(make_response("Invalid resource.", 404))

    logging.warning("mimetype = " + mimetype)

    if mimetype == "application/zip" \
    or mimetype == "application/x-zip" \
    or mimetype == "application/octet-stream" \
    or mimetype == "application/x-zip-compressed":
        resources = addArchive_Zipfile(file)
    else:
        resources = addFile(file)

    return mongodoc_jsonify(resources)


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

@config.g_app.route('/resource/tmp/<resourceId>', methods=['GET'])
def getTmpResource(resourceId):
    '''
    Returns tmp resource file.
    '''
    resource = os.path.join(config.resourcesPath, 'tmp', resourceId)
    return send_file(resource);

@config.g_app.route('/proxy/<resourceId>', methods=['GET'])
def getProxy(resourceId):
    '''
    Returns resource file.
    '''
    resourceName, _ = os.path.splitext(resourceId)
    resource = os.path.join(config.resourcesPath, 'proxy', resourceName + '.png')

    if os.path.isfile(resource):
        return send_file(resource)
    else:
        logging.error("can't find " + resource)
        abort(make_response("can't find " + resource, 404))


@config.g_app.route('/thumbnail/<resourceId>', methods=['GET'])
def getThumbnail(resourceId):
    '''
    Returns resource file.
    '''
    resourceName, _ = os.path.splitext(resourceId)
    resource = os.path.join(config.resourcesPath, 'thumbnail', resourceName + '.png')

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
    return mongodoc_jsonify({"resources": [result for result in resources]})


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


@config.g_app.route('/downloadImgFromUrl', methods=['POST'])
def downloadImgFromUrl():
    '''
    download an image from an url
    '''

    # clean 
    global g_tmpLastClean

    # Clean the cache every interval set in the config
    if g_tmpLastClean < datetime.datetime.now() - datetime.timedelta(hours=config.cleanTmpInterval):
        cache.cleanCache(os.path.join(config.resourcesPath, "tmp"), config.tmpMaxSize)
        # update clean date
        g_tmpLastClean = datetime.datetime.now()

    imgUrl = request.json['url']
    if imgUrl.isspace() or not imgUrl:
        abort(make_response("URL input is empty, please type an URL before to click on send button.", 400))

    if not imgUrl.startswith('http://') and not imgUrl.startswith('https://'):
        imgUrl = 'http://' + imgUrl

    imgId = "tmp/" + str(uuid.uuid4())

    imgPath = os.path.join(config.resourcesPath, imgId)

    try:
        imgData = requests.get(imgUrl)

    except requests.exceptions.ConnectionError as e:
        abort(make_response("The URL that you have sent is not accessible.<br/> Please try again.", 400))

    if not imgData.status_code == requests.codes.ok:
        abort(make_response("The URL that you have sent was not found.", imgData.status_code))

    if not imgData.headers['content-type'].startswith('image'):
        abort(make_response("The URL that you have sent was not an image.<br/> Please try again.", 406))

    if 'gif' in imgData.headers['content-type'] :
        abort(make_response("Sorry, the gif format is not accepted.<br/> Please try again with another image format.", 406))

    imgFile = open(imgPath,'w+')
    imgFile.write(imgData.content)
    imgFile.close()

    ext = imghdr.what(imgPath)

    newImgPath = imgPath + "." + ext

    os.rename(imgPath, newImgPath)

    return imgId + "." + ext

@config.g_app.route('/resource/<resourceId>/plugin/<pluginId>', methods=['POST'])
def addCatalogRessource(resourceId, pluginId):
    '''
    Upload rendered file to the catalog database
    '''

    # Open the rendered file

    renderFile_name = resourceId
    renderFile_path = cache.cachePathFromFile(resourceId)
    if not os.path.isfile(os.path.join(config.renderDirectory, renderFile_path)):
        logging.error(config.renderDirectory + renderFile_path + " doesn't exists")
        abort(make_response(config.renderDirectory + renderFile_path + " doesn't exists", 404))

    renderFile = open(os.path.join(config.renderDirectory, renderFile_path), "rw")
    renderFile.seek(0, os.SEEK_END)
    renderFile_size = renderFile.tell()
    renderFile_mimetype, _ = mimetypes.guess_type(renderFile_name)

    # Add an entry in the db
    uid = config.catalogResourceTable.insert({
        "mimetype" : renderFile_mimetype,
        "size" : renderFile_size,
        "name" : renderFile_name})

    # Write a copy of the rendered file into the catalog with the uid
    # extension = ".png"
    catalogFile_name = str(uid)
    catalogFile_path = os.path.join(config.catalogRootUri, config.catalogResourcesPath, catalogFile_name)

    catalogFile = open(catalogFile_path, "w")
    renderFile.seek(0, 0)
    catalogFile.write(renderFile.read(renderFile_size))
    catalogFile.close()

    renderFile.close()

    resource = config.catalogResourceTable.find_one({"_id": ObjectId(uid)})
    logging.warning("resource = " + str(resource))

    return mongodoc_jsonify(resource)

@atexit.register
def cleanPool():
    '''
    Close processes and quit pool at exit.
    '''
    g_pool.close()
    g_pool.terminate()
    g_pool.join()


if __name__ == '__main__':
    config.g_app.run(host="0.0.0.0", port=5005, debug=True)
