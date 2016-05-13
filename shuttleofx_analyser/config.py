import ConfigParser

from flask import (
    Flask,
    make_response,
    request,
    jsonify,
    abort
)

import multiprocessing


config =  ConfigParser.RawConfigParser()
config.read('/etc/shuttleofx/analyser.cfg')

bundleRootPath = config.get('APP_ANALYSER', 'bundleStore')

g_app = Flask(__name__)

# Pool for analysing jobs 
g_pool = multiprocessing.Pool(processes=4)
g_sharedBundleDatas = {}
g_enablePool = True

# Manager to share analysing information
g_manager = multiprocessing.Manager()
