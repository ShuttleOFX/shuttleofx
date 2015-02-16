#!/usr/bin/python
from flask import Flask, request, jsonify
import uuid, ConfigParser, tarfile, multiprocessing, shutil, os
from multiprocessing import Process
import Bundle

configParser =  ConfigParser.RawConfigParser()
configParser.read('analyzer.cfg')

app = Flask(__name__, static_folder='', static_url_path='')


@app.route('/bundle/<bundleId>', methods=['POST'])
def analyzeBundle(bundleId):
    bundleBin = request.data
    bundleExt = request.headers.get("Content-Type")
    bundle = Bundle.Bundle(bundleId)
    analyzedBundle = None

    if "gzip" == bundleExt.split('/')[1]:
        bundle.extractDatasAsTar(bundleId,bundleBin)
    if "zip" == bundleExt.split('/')[1]:
        bundle.extractDatasAsZip(bundleId,bundleBin)

    analyzedBundle = bundle.analyze()

    return jsonify(**analyzedBundle)

if __name__ == "__main__":
    app.run(host=configParser.get("APP_ANALYZER", "host"), port=configParser.getint("APP_ANALYZER", "port"), debug=True)