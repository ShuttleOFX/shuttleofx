from flask import Flask, jsonify, request, abort, send_file
import json
import requests
import Bundle

# ADD -> for swagger (not done yet)
from flask.ext.restful import Api
from flask_restful_swagger import swagger
#

# ADD -> for postgresql databse
import psycopg2
import sys
import random
import uuid
#

# ADD -> for sqlalchemy using flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
#

app = Flask(__name__)

# ADD
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://webopenfx:tuttle@localhost:5432/webopenfx_db"

db = SQLAlchemy(app)



class Plugin(db.Model, object):
    __tablename__ = 'plugin'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    meta = db.Column(db.String, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    uid = db.Column(UUID)

    def __init__(self):
        super(Plugin, self).__init__()
        self.uid = str(uuid.uuid1())
        self.meta 
        self.name

# ADD
#api = swagger.docs(Api(app), apiVersion='0.1', basePath='http://localhost:5000',)
#

allBundles = {}

def createBundle(metaDatas, pluginsDatas):
    b = Bundle.Bundle()
    b.plugins = pluginsDatas
    b.metaDatas= metaDatas
    return b

#@app.route('/bundle', methods=['POST'])
@app.route('/bundle', methods=['POST'])
def postBundle():
    '''
    Post a bundle object in the DB created with data sent from de the Front server
    '''
    #get the data from the POST request posted from the front
    datas = request.get_json()['metaDatas']
    plugins = request.get_json()['plugins']

    #Creation of a bundle instance with the parameters
    bundle = createBundle(plugins, datas)

    #Insert object in collection
    #collection.insert(bundle.__dict__)

    p = Plugin()
    #p.id = random.randrange(0, 1000000,1)
    p.meta= datas
    p.name= plugins

    db.session.add(p)
    db.session.commit()

    app.logger.info( request.data )
    return jsonify(response="Your bundle as been successfully uploaded")
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    
