#!/usr/bin/python
from flask import Flask, request, jsonify, abort
import uuid, ConfigParser, tarfile, multiprocessing, shutil, os
from multiprocessing import Manager, Pool
import atexit
import Bundle

configParser =  ConfigParser.RawConfigParser()
configParser.read('analyzer.cfg')

g_app = Flask(__name__, static_folder='', static_url_path='')


# Pool for analyzing jobs 
g_pool = multiprocessing.Pool(processes=4)
g_sharedBundleDatas = {}

# Manager to share rendering information
g_manager = Manager()


@g_app.route('/bundle/<bundleId>', methods=['POST'])
def analyzeBundle(bundleId):
    '''
    Apply a pool of process to analyze bundles asynchronously.
    '''
    global g_sharedBundleDatas, g_pool

    bundleBin = request.data
    bundleExt = request.headers.get('Content-Type')

    datas = g_sharedBundleDatas[bundleId] = g_manager.dict()

    datas['globalStatus'] = None
    datas['analyzeStatus'] = None
    datas['extractionStatus'] = None
    datas['datas'] = None

    g_pool.apply(Bundle.launchAnalyze, args=[datas, bundleExt, bundleBin, bundleId])

    return str(True)

@g_app.route('/bundle/<bundleId>', methods=['GET'])
def getStatus(bundleId):
    '''
    Return the analyze status.
    '''

    if bundleId not in g_sharedBundleDatas:
        g_app.logger.error('the id ' + bundleId + ''' doesn't exist''')
        abort (404)

    status = { 'status': g_sharedBundleDatas[bundleId]['globalStatus'], 'extraction': g_sharedBundleDatas[bundleId]['extractionStatus'], 'analyse' : g_sharedBundleDatas[bundleId]['analyzeStatus']}
    return str(status)

@g_app.route('/bundle/<bundleId>/datas', methods=['GET'])
def getBundleDatas(bundleId):
    '''
    Return the analyzed bundle datas.
    '''
    if bundleId not in g_sharedBundleDatas:
        g_app.logger.error('the id ' + bundleId + ''' doesn't exist''')
        abort (404)

    return str(g_sharedBundleDatas[bundleId]['datas'])

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
    g_app.run(host=configParser.get('APP_ANALYZER', 'host'), port=configParser.getint('APP_ANALYZER', 'port'), debug=True)
    
