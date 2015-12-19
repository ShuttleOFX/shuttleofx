import os
import json
import requests
from functools import wraps
from flask import (
    request,
    jsonify,
    render_template,
    abort,
    Response,
    redirect,
    url_for,
    session
)
import logging
import config

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'google_token' in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@config.g_app.errorhandler(404)
def page_not_found(e):
    if 'google_token' in session:
        user = config.google.get('userinfo').data
        return render_template("notFound.html", user=user), 404
    return render_template("notFound.html"), 404


@config.g_app.route('/')
def index():
    if 'google_token' in session:
        user = config.google.get('userinfo').data
        return render_template("index.html", user=user)
    return render_template("index.html")

@config.g_app.route('/plugin')
def getPlugins():
    user = None
    if 'google_token' in session:
        user = config.google.get('userinfo').data
    try:
        resp = requests.get(config.catalogRootUri+"/plugin", params=request.args)
    except:
        return render_template('plugins.html', dico=None, user=user)

    return render_template('plugins.html', dico=resp.json(), user=user)


@config.g_app.route("/plugin/search/")
def searchPlugins():
    user = None
    if 'google_token' in session:
        user = config.google.get('userinfo').data

    resp = requests.get(config.catalogRootUri+"/plugin", params=request.args)

    return render_template('plugins.html', dico=resp.json(), user=user)


@config.g_app.route("/plugin/count")
def countPlugins():
    req = requests.get(config.catalogRootUri+"/plugin", params=request.args)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@config.g_app.route("/plugin/<pluginRawIdentifier>/version/<pluginVersion>")
@config.g_app.route("/plugin/<pluginRawIdentifier>")
def getPlugin(pluginRawIdentifier, pluginVersion="latest"):
    user = None
    if 'google_token' in session:
        user = config.google.get('userinfo').data
    if pluginVersion is "latest":
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier)
       #if resp.status_code == 404:
            #return redirect(url_for('notFoundPage', pluginRawIdentifier=pluginRawIdentifier))
    else:
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier+"/version/"+pluginVersion)
        if resp.status_code == 404:
            return redirect(url_for('getPlugin', pluginRawIdentifier=pluginRawIdentifier))

    if resp.status_code != 200:
        if resp.status_code == 404:
            return render_template('pluginNotFound.html', user=user)
        abort(resp.status_code)
    return render_template('plugin.html', plugin=resp.json(), user=user)

@config.g_app.route('/plugin/<pluginId>/image/<imageId>')
def getSampleImagesForPlugin(pluginId, imageId):
    req = requests.get(config.catalogRootUri + "/resources/" + str(imageId) + "/data")
    return Response(req.content, mimetype=req.headers["content-type"])

@config.g_app.route('/editor')
@config.g_app.route('/editor/<pluginRawIdentifier>')
def renderPageWithPlugin(pluginRawIdentifier):
    user = None
    if 'google_token' in session:
        user = config.google.get('userinfo').data
    resp = requests.get(config.catalogRootUri+"/plugin/"+str(pluginRawIdentifier))
    if resp.status_code != 200:
        abort(resp.status_code)
    previewGallery = requests.get(config.renderRootUri + '/resource/').json()
    return render_template('editor.html', plugin=resp.json(), user=user, resources=previewGallery)

@config.g_app.route('/render', methods=['POST'])
def render():
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Encoding': 'gzip, deflate'
    }
    req = requests.post(config.renderRootUri + "/render", data=request.data, headers=headers)
    return jsonify(**req.json())

@config.g_app.route('/render/<int:renderId>', methods=['GET'])
def getRenderStatus(renderId):
    req = requests.get(config.renderRootUri+"/render/"+str(renderId))
    return jsonify(**req.json())

@config.g_app.route('/render/<renderId>/resource/<resourceId>', methods=['GET'])
def getRenderResource(renderId, resourceId):
    req = requests.get(config.renderRootUri+"/render/"+str(renderId)+"/resource/"+resourceId)
    return Response(req.content, mimetype="image/jpeg")


@config.g_app.route('/resource/<resourceId>', methods=['GET'])
def getResourceById(resourceId):
    req = requests.get(config.renderRootUri+"/resource/"+resourceId)
    return Response(req.content, mimetype="image/png")

@config.g_app.route('/resource', methods=['GET'])
def getResources() :
    req = requests.get(config.renderRootUri + '/resource/')
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@config.g_app.route('/upload')
@login_required
def upload():
    if 'google_token' in session:
        user = config.google.get('userinfo')
        return render_template("upload.html", user=user.data, uploaded=None)
    return redirect(url_for('login'))

@config.g_app.route('/bundle')
def getBundles() :
    req = requests.get(config.catalogRootUri + '/bundle', headers=request.headers)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@config.g_app.route('/bundle', methods=['POST'])
def newBundle() :
    header = {'content-type' : 'application/json'}
    req = requests.post(config.catalogRootUri + '/bundle', data=json.dumps(request.form), headers=header)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@config.g_app.route('/bundle/<bundleId>/archive', methods=['POST'])
def uploadArchive(bundleId):
    filename = request.files['file'].filename
    file = request.files['file']

    file.save("/tmp/" + filename)
    multiple_files = [('file', (filename, open("/tmp/" + filename, 'rb'), 'application/gzip'))]

    req = requests.post(config.catalogRootUri + '/bundle/' + bundleId + '/archive', files = multiple_files)
    if req.status_code != 200:
        abort(req.status_code)
    os.remove("/tmp/" + filename)
    return jsonify(**req.json())

@config.g_app.route('/bundle/<bundleId>/analyse', methods=['POST'])
def analyseBundle(bundleId):
    req = requests.post(config.catalogRootUri + '/bundle/' + bundleId + '/analyse', data=request.data, headers=request.headers)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@config.g_app.route('/login')
def login():
    logging.warning('login start')
    res = config.google.authorize(callback=url_for('authorized', _external=True))
    logging.warning('login end')
    return res


@config.g_app.route('/logout')
def logout():
    session.pop('google_token', None)
    redirectTarget = request.values.get('next') or request.referrer
    return redirect( redirectTarget )


@config.g_app.route('/login/authorized')
def authorized():
    logging.warning('login/authorized start')
    resp = config.google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (resp['access_token'], '')
    # user = config.google.get('userinfo')

    aa = {(k, v) for (k, v) in request.args.iteritems()}
    logging.warning('login/authorized request.args:', str(aa))

    redirectTarget = request.values.get('next') or request.referrer or url_for('getPlugins')
    if redirectTarget == None:
        logging.warning('login/authorized redirectTarget is None')

    logging.warning('login/authorized before redirect')
    res = redirect( redirectTarget )
    logging.warning('login/authorized end')
    return res


@config.g_app.route("/plugin/<int:pluginId>/resource", methods=['POST'])
def addPluginResource(pluginId):
    filename = request.files['file'].filename
    file = request.files['file']
    file.save("/tmp/" + filename)

    multiple_files = [('file', (filename, open("/tmp/"+filename, 'rb'), 'application/gzip'))]

    req = requests.post(config.catalogRootUri + "/resources", files = multiple_files)

    return jsonify(**req.json())

@config.g_app.route("/plugin/<int:pluginId>/images", methods=['POST'])
def addImageToPlugin(pluginId):
    req = requests.post(config.catalogRootUri + "/plugin/" + str(pluginId) + "/images", data=request.data, headers=request.headers)
    return jsonify(**req.json())

@config.google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    config.g_app.run(host="0.0.0.0",port=5000,debug=True)
