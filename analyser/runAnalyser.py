#!/usr/bin/python
from flask import Flask, request, jsonify, abort
import os
import ConfigParser
import multiprocessing
import atexit
import Bundle

currentAppDir = os.path.dirname(__file__)

configParser =  ConfigParser.RawConfigParser()
configParser.read( os.path.join( currentAppDir, 'analyser.cfg' ) )

g_app = Flask(__name__, static_folder='', static_url_path='')


# Pool for analysing jobs 
g_pool = multiprocessing.Pool(processes=4)
g_sharedBundleDatas = {}
g_enablePool = True

# Manager to share analysing information
g_manager = multiprocessing.Manager()

@g_app.route('/', methods=['GET'])
def index():
    return "Analyser service v1.0"

@g_app.route('/bundle/<bundleId>', methods=['POST'])
def analyseBundle(bundleId):
    '''
    Apply a pool of process to analyse bundles asynchronously.
    '''
    global g_sharedBundleDatas, g_pool, g_enablePool

    bundleBin = request.data
    bundleExt = request.headers.get('Content-Type')

    datas = g_sharedBundleDatas[bundleId] = g_manager.dict()

    datas['status'] = "waiting"
    datas['analyse'] = "waiting"
    datas['extraction'] = "waiting"
    datas['datas'] = None

    if g_enablePool:
        g_pool.apply(Bundle.launchAnalyse, args=[datas, bundleExt, bundleBin, bundleId])
    else:
        Bundle.launchAnalyse(datas, bundleExt, bundleBin, bundleId)

    return jsonify(**datas)

@g_app.route('/bundle/<bundleId>', methods=['GET'])
def getStatus(bundleId):
    '''
    Return the analyse status.
    '''
    global g_sharedBundleDatas
    if bundleId not in g_sharedBundleDatas:
        g_app.logger.error('the id ' + bundleId + ''' doesn't exist''')
        abort (404)

    return jsonify(**g_sharedBundleDatas[bundleId])

@atexit.register
def quit():
    '''
    Close processes and quit pool at exit.
    '''
    global g_pool
    g_pool.close()
    g_pool.terminate()
    g_pool.join()

if __name__ == '__main__':
    g_app.run(host=configParser.get('APP_ANALYSER', 'host'), port=configParser.getint('APP_ANALYSER', 'port'), debug=True)
