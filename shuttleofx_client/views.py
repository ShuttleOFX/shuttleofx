import os
import json
import requests
import shutil
import tempfile
from functools import wraps
from flask import (
	request,
	jsonify,
	render_template,
	abort,
	Response,
	redirect,
	url_for,
	session,
	make_response,
    send_file
)
from subprocess import (check_call, check_output, CalledProcessError)
import logging
import config
import userManager

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        user = userManager.getUser()
        if user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@config.g_app.errorhandler(404)
def page_not_found(e):
    user = userManager.getUser()
    if user is not None:
        return render_template("notFound.html", user=user), 404
    return render_template("notFound.html"), 404


@config.g_app.route('/')
def index():
    user = userManager.getUser()
    if user is not None:
        return render_template("home.html", user=user)
    return render_template("home.html")


@config.g_app.route('/plugin')
def getPlugins():
    user = userManager.getUser()
    try:
        resp = requests.get(config.catalogRootUri+"/plugin", params=request.args)
    except:
        return render_template('plugins.html', dico=None, user=user)

    return render_template('plugins.html', dico=resp.json(), user=user)


@config.g_app.route('/plugins')
def getAllPlugins():
    req = requests.get(config.catalogRootUri+"/plugins")
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@config.g_app.route('/about')
def getInfo():
    user = userManager.getUser()
    if user is not None:
        return render_template('whatIsOFX.html', user=user)
    return render_template('whatIsOFX.html', user=user)


@config.g_app.route("/plugin/search")
def searchPlugins():
    user = userManager.getUser()

    resp = requests.get(config.catalogRootUri+"/plugin", params=request.args)

    return render_template('plugins.html', dico=resp.json(), user=user)


@config.g_app.route("/plugin/count")
def countPlugins():
    req = requests.get(config.catalogRootUri + "/plugin", params=request.args)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())


@config.g_app.route("/plugin/<pluginRawIdentifier>/version/<pluginVersion>")
@config.g_app.route("/plugin/<pluginRawIdentifier>")
def getPlugin(pluginRawIdentifier, pluginVersion="latest"):
    user = userManager.getUser()
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
    return render_template('plugin.html', plugin=resp.json()['plugin'], versions=resp.json()['versions'], user=user)


@config.g_app.route("/plugin/<pluginRawIdentifier>/info")
@config.g_app.route("/plugin/<pluginRawIdentifier>/version/<pluginVersion>/info")
def getPluginInfo(pluginRawIdentifier, pluginVersion="latest"):
    user = userManager.getUser()

    if pluginVersion is "latest":
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier)
       #if resp.status_code == 404:
            #return redirect(url_for('notFoundPage', pluginRawIdentifier=pluginRawIdentifier))
    else:
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier+"/version/"+pluginVersion)
        if resp.status_code == 404:
            return redirect(url_for('getPlugin', pluginRawIdentifier=pluginRawIdentifier))

    return render_template('pluginInfo.html', plugin=resp.json()['plugin'], versions=resp.json()['versions'], user=user)

@config.g_app.route("/plugin/<int:pluginId>/version/<pluginVersion>/download/<bundleId>")
@config.g_app.route("/plugin/<int:pluginId>/download/<bundleId>")
def downloadPlugin(pluginId, bundleId, pluginVersion="latest"):
    if pluginVersion is "latest":
        req = requests.get(config.catalogRootUri+"/plugin/"+str(pluginId)+"/download/"+str(bundleId))
    else:
        req = requests.get(config.catalogRootUri+"/plugin/"+str(pluginId)+"/version/"+pluginVersion+"/download/"+str(bundleId))
    if req.status_code != requests.codes.ok:
        abort(make_response(req.content, req.status_code))

    content = json.loads(req.content)
    filename = 'Bundle_' + content['bundleId'] + '.' + content['fileExtension']
    return send_file(content['filePath'], as_attachment=True, attachment_filename=filename)

@config.g_app.route('/plugin/<pluginId>/image/<imageId>')
def getSampleImagesForPlugin(pluginId, imageId):
    req = requests.get(config.catalogRootUri + "/resources/" + str(imageId) + "/data")
    return Response(req.content, mimetype=req.headers["content-type"])

@config.g_app.route('/plugin/<pluginId>/thumbnail/<imageId>')
def getSampleThumbnailForPlugin(pluginId, imageId):
    req = requests.get(config.catalogRootUri + "/resources/" + str(imageId) + "/thumbnail")
    return Response(req.content, mimetype=req.headers["content-type"])


@config.g_app.route('/category')
def getCategory():
    user = userManager.getUser()
    try:
        resp = requests.get(config.catalogRootUri + "/category", params=request.args)
    except:
        return render_template('plugins.html', dico=None, user=user)

    return render_template('plugins.html', dico=resp.json(), user=user)

@config.g_app.route('/demo')
@config.g_app.route('/plugin/<pluginRawIdentifier>/demo')
@config.g_app.route("/plugin/<pluginRawIdentifier>/version/<pluginVersion>/demo")
def renderPageWithPlugin(pluginRawIdentifier, pluginVersion="latest"):
    user = userManager.getUser()

    if pluginVersion is "latest":
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier)
       #if resp.status_code == 404:
            #return redirect(url_for('notFoundPage', pluginRawIdentifier=pluginRawIdentifier))
    else:
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier+"/version/"+pluginVersion)
        if resp.status_code == 404:
            return redirect(url_for('getPlugin', pluginRawIdentifier=pluginRawIdentifier))

    if resp.status_code != 200:
        abort(resp.status_code)
    previewGallery = requests.get(config.renderRootUri + '/resource/').json()

    if pluginRawIdentifier == 'tuttle.ctl':
        return render_template('scriptEditor.html', plugin=resp.json(), user=user, resources=previewGallery)

    return render_template('editor.html', plugin=resp.json()['plugin'], versions=resp.json()['versions'], user=user, resources=previewGallery)

### Wiki Start _________________________________________________________________
@config.g_app.route("/plugin/<pluginRawIdentifier>/version/<pluginVersion>/wiki")
@config.g_app.route("/plugin/<pluginRawIdentifier>/wiki")
def getPluginWiki(pluginRawIdentifier, pluginVersion="latest"):
    user = userManager.getUser()
    if pluginVersion is "latest":
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier)
    else:
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier+"/version/"+pluginVersion)
        if resp.status_code == 404:
            return redirect(url_for('getPlugin', pluginRawIdentifier=pluginRawIdentifier))
    if resp.status_code != 200:
        if resp.status_code == 404:
            return render_template('notFound.html', user=user)
        abort(resp.status_code)
    return render_template('wiki.html', plugin=resp.json()['plugin'], versions=resp.json()['versions'],user=user)

@config.g_app.route("/wiki/edit/<pluginRawIdentifier>/version/<pluginVersion>")
@config.g_app.route("/wiki/edit/<pluginRawIdentifier>")
def getPluginWikiEdit(pluginRawIdentifier, pluginVersion="latest"):
    user = userManager.getUser()
    if pluginVersion is "latest":
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier)
    else:
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier+"/version/"+pluginVersion)
        if resp.status_code == 404:
            return redirect(url_for('getPlugin', pluginRawIdentifier=pluginRawIdentifier))
    if resp.status_code != 200:
        if resp.status_code == 404:
            return render_template('notFound.html', user=user)
        abort(resp.status_code)
    return render_template('wikiedit.html', plugin=resp.json()['plugin'], versions=resp.json()['versions'], user=user)

@config.g_app.route('/wiki/update/<pluginId>/version/<pluginVersion>', methods=['POST'])
@config.g_app.route('/wiki/update/<pluginId>', methods=['POST'])
def setWiki(pluginId, pluginVersion="latest"):
    user = userManager.getUser()
    header = {'content-type' : 'application/json'}
    req = requests.post(config.catalogRootUri + "/wiki/update/" + pluginId, data=request.data, headers=header)
    return req.content

### Wiki End ___________________________________________________________________

### Comments Start _____________________________________________________________

@config.g_app.route("/plugin/<pluginRawIdentifier>/version/<pluginVersion>/comments")
@config.g_app.route("/plugin/<pluginRawIdentifier>/comments")
def getPluginComments(pluginRawIdentifier, pluginVersion="latest"):
    user = userManager.getUser()
    if pluginVersion is "latest":
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier)
    else:
        resp = requests.get(config.catalogRootUri+"/plugin/"+pluginRawIdentifier+"/version/"+pluginVersion)
        if resp.status_code == 404:
            return redirect(url_for('getPlugin', pluginRawIdentifier=pluginRawIdentifier))
    if resp.status_code != 200:
        if resp.status_code == 404:
            return render_template('notFound.html', user=user)
        abort(resp.status_code)
    return render_template('comments.html', plugin=resp.json()['plugin'], versions=resp.json()['versions'], user=user)

@config.g_app.route('/plugin/<pluginId>/version/<pluginVersion>/comments/update', methods=['POST'])
@config.g_app.route('/plugin/<pluginId>/comments/update', methods=['POST'])
def addComment(pluginId, pluginVersion="latest"):
    user = userManager.getUser()
    header = {'content-type' : 'application/json'}
    req = requests.post(config.catalogRootUri + "/plugin/" + pluginId + "/comments/update", data=request.data, headers=header)
    return req.content

### Comments End _______________________________________________________________

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
    req = requests.get(config.renderRootUri + "/resource/" + resourceId)
    return Response(req.content, mimetype="image/png")


@config.g_app.route('/proxy/<resourceId>', methods=['GET'])
def getProxyById(resourceId):
    req = requests.get(config.renderRootUri + "/proxy/" + resourceId)
    return Response(req.content, mimetype="image/png")

@config.g_app.route('/thumbnail/<resourceId>', methods=['GET'])
def getThumbnailById(resourceId):
    req = requests.get(config.renderRootUri + "/thumbnail/" + resourceId)
    return Response(req.content, mimetype="image/png")

@config.g_app.route('/resource/tmp/<resourceId>', methods=['GET'])
def getTmpResourceById(resourceId):
    req = requests.get(config.renderRootUri+"/resource/tmp/"+resourceId)
    return Response(req.content)

@config.g_app.route('/resource', methods=['GET'])
def getResources():
    req = requests.get(config.renderRootUri + '/resource/')
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())


@config.g_app.route('/upload')
def upload():
    user = userManager.getUser()
    return render_template("upload.html", user=user, uploaded=None)

@config.g_app.route('/upload/automated/<token>', methods=['POST'])
def uploadAutomated(token):
    # FIXME Upload need to be refactored to be able to do it with only one route
    #       and thus avoid rewriting the same code in this function
    # COMMAND : curl -s -o /dev/null -w "%{http_code}" -X POST -F 'file=@/home/olivier/Downloads/CImg.tar.gz' http://localhost/upload/automated/1
    logging.warning('Automated upload started')
    if token is None:
        abort(400)
    # Set metadata
    headerJSON = {'content-type' : 'application/json'}
    bundleInfo = {"bundleName": '', 'bundleDescription': '', 'userId': token, 'companyId': ''}
    # Create bundle in DB
    req = requests.post(config.catalogRootUri + '/bundle', data=json.dumps(bundleInfo), headers=headerJSON)
    if req.status_code != 200:
        abort(req.status_code)

    resp = req.json()
    bundleId = str(resp.get('bundleId'))
    # Save file sent by users
    filename = request.files['file'].filename
    file = request.files['file']
    file.save("/tmp/" + filename)
    multiple_files = [('file', (filename, open("/tmp/" + filename, 'rb'), 'application/gzip'))]

    # Process bundle
    req = requests.post(config.catalogRootUri + '/bundle/' + bundleId + '/archive', files = multiple_files)
    if req.status_code != 200:
        abort(req.status_code)
    req = requests.post(config.catalogRootUri + '/bundle/' + bundleId + '/analyse', data = bundleInfo, headers = headerJSON)
    if req.status_code != 200:
        abort(req.status_code)

    return Response(status=200)

@config.g_app.route('/bundle')
def getBundles():
    req = requests.get(config.catalogRootUri + '/bundle', headers=request.headers)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())


@config.g_app.route('/bundle', methods=['POST'])
def newBundle():
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
    req = requests.post(config.catalogRootUri + '/bundle/' + bundleId + '/analyse', data=request.data,
                        headers=request.headers)

    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())


@config.g_app.route('/login/google')
def loginGoogle():
    logging.warning('login start')
    res = config.google.authorize(callback=url_for('authorizedGoogle', _external=True))
    logging.warning('login end')
    return res

@config.g_app.route('/login/github')
def loginGithub():
    res = config.github.authorize(callback=url_for('authorizedGithub', _external=True))
    return res

@config.g_app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('github_token', None)
    redirectTarget = request.values.get('next') or request.referrer
    return redirect( redirectTarget )

@config.g_app.route('/login/authorized/google')
def authorizedGoogle():
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
    res = redirect(redirectTarget)
    logging.warning('login/authorized end')
    return res


@config.g_app.route('/login/authorized/github')
def authorizedGithub():
    resp = config.github.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['github_token'] = (resp['access_token'], '')
    # First connexion when you authorize access to your Github account
    if request.referrer == 'https://github.com/':
        redirectTarget = url_for('getPlugins')
    else:
        redirectTarget = request.values.get('next') or request.referrer or url_for('getPlugins')
    if redirectTarget == None:
        logging.warning('login/authorized redirectTarget is None')

    res = redirect( redirectTarget )
    return res


@config.g_app.route("/plugin/<int:pluginId>/resource", methods=['POST'])
def addPluginResource(pluginId):
    filename = request.files['file'].filename
    file = request.files['file']
    file.save("/tmp/" + filename)

    multiple_files = [('file', (filename, open("/tmp/" + filename, 'rb'), 'application/gzip'))]

    req = requests.post(config.catalogRootUri + "/resources", files=multiple_files)

    return jsonify(**req.json())


@config.g_app.route("/plugin/<int:pluginId>/images", methods=['POST'])
def addImageToPlugin(pluginId):
    req = requests.post(
        config.catalogRootUri + "/plugin/" + str(pluginId) + "/images",
        data=request.data, headers=request.headers)
    return jsonify(**req.json())


@config.g_app.route("/plugin/<int:pluginId>/render/<renderId>/resource/<resourceId>", methods=['POST'])
def addRenderToPlugin(pluginId, resourceId, renderId):

    # get rendered image
    req = requests.get(config.renderRootUri + "/render/" + renderId + "/resource/" + resourceId)

    filename = resourceId
    file = open("/tmp/" + filename, "w")
    file.seek(0, 0)
    file.write(req.content)
    file.close()

    multiple_files = [("file", (filename, open("/tmp/" + filename, 'rb'), 'application/gzip'))]

    # send rendered image to catalog
    req = requests.post(config.catalogRootUri + "/resources", files=multiple_files)

    os.remove("/tmp/" + filename)

    content = json.loads(req.content)
    logging.warning("content = " + str(content))
    imageId = content["_id"]["$oid"]

    # link rendered image to plugin in catalog
    headers = {u'content-type': 'application/json'}
    data = {u'ressourceId': imageId}
    req = requests.post(
        config.catalogRootUri + "/plugin/" + str(pluginId) + "/images",
        data=json.dumps(data), headers=headers)

    return jsonify(**req.json())


@config.g_app.route("/plugin/<int:pluginId>/defaultImage/<imageId>", methods=['POST'])
def setPluginDefaultImage(pluginId, imageId):
    req = requests.post(
        config.catalogRootUri + "/plugin/" + str(pluginId) + "/defaultImage/" + str(imageId),
        data=request.data, headers=request.headers)
    return jsonify(**req.json())


@config.g_app.route('/downloadImgFromUrl', methods=['POST'])
def downloadImgFromUrl():
    '''
    download an image from an url
    '''
    header = {'content-type' : 'application/json'}
    req = requests.post(config.renderRootUri + "/downloadImgFromUrl", data=request.data, headers=header)

    if req.status_code != requests.codes.ok:
        abort(make_response(req.content, req.status_code))

    return req.content

@config.google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@config.github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')

@config.g_app.route('/create')
def createPlugin():
    user = userManager.getUser()
    provider = userManager.getOAuthProvider()
    return render_template("createPlugin.html", user=user, provider=provider)

@config.g_app.route('/create/repo', methods=['POST'])
def createUserRepo():
    user = userManager.getUser()
    provider = userManager.getOAuthProvider()
    githubToken = session['github_token'][0]
    if githubToken is None:
        status = 'error'
        message = 'You are trying to create a repository without being logged using Github.'

    pluginTemplatePath = ''
    try:
        pluginTemplatePath = downloadPluginTemplateRepo(False)
        pluginName = request.form['pluginName']
        #Create user's repo
        req = config.github.post('/user/repos', data={
            "name": pluginName,
            "private": False,
        }, format='json')

        owner = req.data['owner']['login']

        # Enable Travis
        check_call(['travis', 'login', '--github-token', str(githubToken)], cwd=pluginTemplatePath)
        check_call(['travis', 'enable', '-r', owner +'/'+ pluginName ], cwd=pluginTemplatePath)
        check_call(['travis', 'env', 'set', 'TOKEN', str(githubToken), '--private', '-r', owner +'/'+ pluginName])

        # Push on user's repo
        url = 'https://' + owner + ':' + session['github_token'][0] + '@github.com' +'/'+ owner +'/'+ pluginName + '.git'
        check_call(['git', 'remote', 'add', 'origin', url], cwd=pluginTemplatePath)
        check_call(['git', 'remote', '-v'], cwd=pluginTemplatePath)
        check_call(['git', 'push', 'origin', 'master'], cwd=pluginTemplatePath)

        # Delete cloned repo
        shutil.rmtree(pluginTemplatePath)


        return render_template("createPluginSuccess.html", userGithubAlias=owner, repoName=request.form['pluginName'])
    except CalledProcessError:
        status = 'error'
        message = 'There was an error creating your repository, please try again.'
        # Ensure to clean even if the process has failed
        if os.path.isdir(pluginTemplatePath):
            shutil.rmtree(pluginTemplatePath)

        return render_template("createPlugin.html", user=user, provider=provider, status=status, message=message)

@config.g_app.route('/create/sources', methods=['POST'])
def downloadPluginTemplate():
    pluginTemplatePath = ''
    try:
        pluginTemplatePath = downloadPluginTemplateRepo(True)

        shutil.make_archive(pluginTemplatePath, 'zip', pluginTemplatePath)
        # Delete cloned repo
        shutil.rmtree(pluginTemplatePath)

        return send_file(pluginTemplatePath + '.zip', as_attachment=True, attachment_filename="OpenFX_plugin_template.zip")
    except CalledProcessError:
        user = userManager.getUser()
        provider = userManager.getOAuthProvider()
        status = 'error'
        message = 'There was an error creating your customized plugin, please try again.'

        # Ensure to clean even if the process has failed
        if os.path.isdir(pluginTemplatePath):
            shutil.rmtree(pluginTemplatePath)

        return render_template("createPlugin.html", user=user, provider=provider, status=status, message=message)


def downloadPluginTemplateRepo(submodule=False):
    pluginTemplatePath = tempfile.mkdtemp()
    try:
        # Create new repo from project template (squash all commits into one to get a clean history)
        check_call(['git', 'init'], cwd=pluginTemplatePath)
        check_call(['git', 'fetch', '--depth=1', '-n', 'https://github.com/tuttleofx/ofxPluginTemplate.git'], cwd=pluginTemplatePath)
        output = check_output(['git', 'commit-tree', 'FETCH_HEAD^{tree}', '-m', 'Initial Openfx structure'], cwd=pluginTemplatePath).strip()
        check_call(['git', 'reset', '--hard', output], cwd=pluginTemplatePath)

        # Replace template data with user's data
        jsonFile = repoFormToJSON(request)
        check_call(['python','createPlugin.py', jsonFile, './'], cwd=pluginTemplatePath)
        if submodule:
            check_call(['git', 'submodule', 'update', '-i'], cwd=pluginTemplatePath)
        # Remove createPlugin.py and the JSON used to replace data with user's data
        os.remove(os.path.join(pluginTemplatePath,'createPlugin.py'))
        os.remove(jsonFile)

        check_call(['git', 'add', '-A'], cwd=pluginTemplatePath)
        check_call(['git', 'commit', '--amend', '-m', 'Initial Openfx structure'], cwd=pluginTemplatePath)
    except CalledProcessError as e:
        raise CalledProcessError(e.returncode, e.cmd, e.output)

    return pluginTemplatePath

def repoFormToJSON(request):
    pluginLabel = request.form["pluginLabel"]
    pluginLongLabel = request.form["pluginLongLabel"]

    if not request.form["pluginLabel"]:
        pluginLabel = request.form["pluginName"]
    else:
        pluginLabel = request.form["pluginLabel"]

    if not request.form["pluginLongLabel"]:
        pluginLongLabel = request.form["pluginName"]
    else:
        pluginLongLabel = request.form["pluginLongLabel"]

    filePath = os.path.join(os.sep, 'tmp', 'JSONForm.json')
    JSONFile, JSONFilePath = tempfile.mkstemp()
    json.dump({"PLUGIN_NAME": str(request.form['pluginName']),
               "PLUGIN_LABEL": str(pluginLabel),
               "PLUGIN_LONG_LABEL": str(pluginLongLabel),
               "PLUGIN_GROUPING": str(request.form["pluginMenu"]),
               "PLUGIN_UID": str(request.form["id"]),
               "PLUGIN_DESCRIPTION": str(request.form["pluginDescription"])}, os.fdopen(JSONFile, 'w'))

    return JSONFilePath

if __name__ == '__main__':
    config.g_app.run(host="0.0.0.0", port=5000, debug=True)
