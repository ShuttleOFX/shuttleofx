import uuid
from datetime import datetime

from flask import Flask
import psycopg2

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON


app = Flask(__name__)

# ADD
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://webopenfx:tuttle@localhost:5432/webopenfx_db"

db = SQLAlchemy(app)

class Bundle(object):
    '''
    This the representation of a Bundle.
    '''

    __tablename__ = 'bundle'
    '''
    Representation of a Bundle in the DB
    '''
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    bundleID = db.Column(UUID, nullable = False)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    companyID = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.String(250))
    uploadDate = db.Column(db.DateTime, nullable = False)
    shared = db.Column(db.Boolean, nullable = False)
    contributors = db.Column(ARRAY(db.Integer))
    architecture = db.Column(ARRAY(db.String), nullable=False)
    plugins = db.Column(ARRAY(db.Integer), nullable=False)
    uploaded = db.Column(db.Boolean, nullable=False)

    def __init__(self):
        '''
        Constructor for a Bundle
        '''
        super(Bundle, self).__init__()
        self.uid = str(uuid.uuid1())
        self.uploadDate = datetime.now()
        self.shared = False
        self.uploaded = False

db.create_all()
db.session.commit()
