#!/usr/bin/python

import ConfigParser
import requests
import json
from functools import wraps
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    abort,
    Response,
    redirect,
    url_for,
    session
    )
from flask_oauthlib.client import OAuth

app = Flask(__name__)

configParser =  ConfigParser.ConfigParser()
configParser.read('client.cfg')

googleId =configParser.get('OAUTH_CONFIG', 'googleId')
googleSecret =configParser.get('OAUTH_CONFIG', 'googleSecret')


app.config['GOOGLE_ID'] = googleId
app.config['GOOGLE_SECRET'] = googleSecret
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.profile'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

catalogRootUri = configParser.get("APP_CLIENT", "catalogRootUri")
renderRootUri  = configParser.get("APP_CLIENT", "renderRootUri")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'google_token' in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
# @login_required
def index():
    if 'google_token' in session:
        user = google.get('userinfo').data
        return render_template("index.html", user=user)
    return render_template("index.html")

@app.route('/plugin')
def getPlugins():
    user = None
    if 'google_token' in session:
        user = google.get('userinfo').data
    try:
        resp = requests.get(catalogRootUri+"/plugin", params=request.args)
    except:
        return render_template('plugins.html', dico=None, user=user)

    return render_template('plugins.html', dico=resp.json(), user=user)

@app.route('/plugin/<pluginId>')
def getPlugin(pluginId):
    user = None
    if 'google_token' in session:
        user = google.get('userinfo').data
    resp = requests.get(catalogRootUri+"/plugin/"+pluginId)
    return render_template('plugin.html', plugin=resp.json(), user=user)

@app.route('/plugin/<pluginId>/image/<imageId>')
def getSampleImagesForPlugin(pluginId, imageId):
    req = requests.get(catalogRootUri + "/resources/" + str(imageId) + "/data")
    return Response(req.content, mimetype=req.headers["content-type"])

@app.route('/editor')
def renderPage():
    user = None
    if 'google_token' in session:
        user = google.get('userinfo').data
    resp = requests.get(catalogRootUri+"/plugin/0")
    return render_template('editor.html', plugin=resp.json(), user=user)

@app.route('/editor/<pluginId>')
def renderPageWithPlugin(pluginId):
    user = None
    if 'google_token' in session:
        user = google.get('userinfo').data
    resp = requests.get(catalogRootUri+"/plugin/"+pluginId)
    return render_template('editor.html', plugin=resp.json(), user=user)

@app.route('/render', methods=['POST'])
def render():
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Encoding': 'gzip, deflate'
    }
    req = requests.post(renderRootUri + "/render", data=request.data, headers=headers)
    return jsonify(**req.json())

@app.route('/render/<int:renderId>', methods=['GET'])
def getRenderStatus(renderId):
    req = requests.get(renderRootUri+"/render/"+str(renderId))
    return jsonify(**req.json())

@app.route('/render/<renderId>/resource/<resourceId>', methods=['GET'])
def getRenderResource(renderId, resourceId):
    req = requests.get(renderRootUri+"/render/"+str(renderId)+"/resource/"+resourceId)
    return Response(req.content, mimetype="image/jpeg")

@app.route('/upload')
@login_required
def upload():
    if 'google_token' in session:
        user = google.get('userinfo')
        return render_template("upload.html", user=user.data)
    return redirect(url_for('login'))
    #return render_template('upload.html', uploaded=None)

@app.route('/bundle')
def getBundles() :
    req = requests.get(catalogRootUri + '/bundle', headers=request.headers)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@app.route('/bundle', methods=['POST'])
def newBundle() :
    header = {'content-type' : 'application/json'}
    req = requests.post(catalogRootUri + '/bundle', data=json.dumps(request.form), headers=header)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@app.route('/bundle/<bundleId>/archive', methods=['POST'])
def uploadArchive(bundleId):
    req = requests.post(catalogRootUri + '/bundle/' + bundleId + '/archive', data=request.data, headers=request.headers)
    if req.status_code != 200:
        abort(req.status_code)
    return jsonify(**req.json())

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    print resp
    session['google_token'] = (resp['access_token'], '')
    user = google.get('userinfo')
    return render_template("index.html", user=user.data)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == "__main__":
    app.run(host=configParser.get("APP_CLIENT", "host"), port=configParser.getint("APP_CLIENT", "port"), debug=True)
