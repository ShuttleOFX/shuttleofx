#!/usr/bin/python

import sys
import json
import argparse
import requests


def upload(archive, metadata, catalogURI):
    '''
    Upload an archived bundle on the shuttleOFX DB.
    '''

    headerGzip = {'Content-type': 'application/gzip'}
    headerJson= {'Content-type': 'application/json'}

    resp = requests.post(catalogURI+"/bundle", data=json.dumps(metadata), headers=headerJson)
    print resp.text
    resp = resp.json()
    bundleId = str(resp.get('bundleId'))

    resp = requests.post(catalogURI+"/bundle/"+bundleId+"/archive", data=open(archive, 'r').read(), headers=headerGzip)
    print resp.text
    resp = requests.post(catalogURI+"/bundle/"+bundleId+"/analyse", data=metadata, headers=headerJson)
    print resp.text

if __name__ == "__main__":
    '''
    Parse commande line arguments and call the upload function with the arguments.
    '''
    parser = argparse.ArgumentParser(description='Upload an OpenFX bundle to the ShuttleOFX platform.')
    parser.add_argument('-n', '--name', metavar='BUNDLE_NAME', type=str,
                       help='')
    parser.add_argument('-u', '--userId', metavar='USER', type=int,
                       help='')
    parser.add_argument('-c', '--companyId', metavar='COMPANY', type=int,
                       help='')
    parser.add_argument('--uri', metavar='CATALOG_URI', type=str,
                       help='')
    parser.add_argument('file', metavar='FILEPATH', type=str,
                       help='')

    args = parser.parse_args()

    metadata = {
        "name": args.name,
        "userId": args.userId,
        "companyId" : args.companyId,
    }

    upload(args.file, metadata, args.uri)
