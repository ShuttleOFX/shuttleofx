import ConfigParser
import logging

from flask_oauthlib.client import OAuth

import os
import json
import requests
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

config =  ConfigParser.ConfigParser()
config.read('/etc/shuttleofx/client.cfg')

g_app = Flask(__name__)

g_app.config['GOOGLE_ID'] = config.get('OAUTH_CONFIG', 'googleId')
g_app.config['GOOGLE_SECRET'] = config.get('OAUTH_CONFIG', 'googleSecret')
g_app.config['GITHUB_ID'] = config.get('OAUTH_CONFIG', 'githubId')
g_app.config['GITHUB_SECRET'] = config.get('OAUTH_CONFIG', 'githubSecret')
g_app.debug = True
g_app.secret_key = 'development'

oauth = OAuth(g_app)

google = oauth.remote_app(
    'google',
    consumer_key=g_app.config.get('GOOGLE_ID'),
    consumer_secret=g_app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.profile'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

github = oauth.remote_app(
    'github',
    consumer_key=g_app.config.get('GITHUB_ID'),
    consumer_secret=g_app.config.get('GITHUB_SECRET'),
    access_token_method='POST',
    base_url='https://api.github.com/user',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    request_token_params={'scope': 'public_repo'}
)

def get_resource_as_string(name, charset='utf-8'):
    with g_app.open_resource(name) as f:
        return f.read().decode(charset)

g_app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

catalogRootUri = config.get("APP_CLIENT", "catalogRootUri")
renderRootUri  = config.get("APP_CLIENT", "renderRootUri")
