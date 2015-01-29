import uuid , ConfigParser , psycopg2
from datetime import datetime

from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON

configParser = ConfigParser.RawConfigParser()
configParser.read('configuration.conf')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://"+configParser.get("DB_CONFIG", "dbUser")+":"+configParser.get("DB_CONFIG", "dbMdp")+"@"+configParser.get("DB_CONFIG", "dbUrl")+"/"+configParser.get("DB_CONFIG", "dbName")

db = SQLAlchemy(app)


'''
Note that this is a work in progress version : 
- When there is relations between tables, they need (for know) to be declared in the same file
- I will work on a cleaner strucure once the plugins are recorded in the db
- Also, to make the relations work, we need to have different columns names. Prefixing with the table name isn't enough
'''

class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}
 
    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class Bundle(db.Model, Serializer):
    '''
    This the representation of a Bundle.
    '''

    __tablename__ = 'bundle'
    '''
    Representation of a Bundle in the DB
    '''
    bundleId = db.Column(db.Integer, primary_key = True)
    bundleUid = db.Column(UUID, nullable = False, unique=True)
    #userId = db.relationship('User', lazy='dynamic', uselist=False )
    # Will change when authentification will be implemented
    userId = db.Column(db.Integer, nullable = False)
    #companyId = db.relationship('Company', backref='bundle', lazy='dynamic', uselist=False )
    companyId = db.Column(db.Integer)
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.String(250))
    uploadDate = db.Column(db.DateTime, nullable = False)
    shared = db.Column(db.Boolean, nullable = False)
    contributors = db.Column(ARRAY(db.Integer))
    architecture = db.Column(ARRAY(db.String))
    plugins = db.Column(ARRAY(db.Integer))
    uploaded = db.Column(db.Boolean, nullable=False)
 
    def __init__(self):
        '''
        Constructor for a Bundle
        '''
        super(Bundle, self).__init__()
        self.bundleUid = str(uuid.uuid1())
        self.uploadDate = datetime.now()
        self.shared = False
        self.uploaded = False
 
    def serialize(self):
           return Serializer.serialize(self)


class User(db.Model, Serializer):
    '''
    This the representation of a User.
    '''
 
    __tablename__ = 'user'
    '''
    Representation of a User in the DB
    '''
    userId = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    firstname = db.Column(db.String, nullable = False)
    mail = db.Column(db.String, nullable = False)
    company = db.Column(ARRAY(db.Integer), nullable = False)
    #Will change when identification will be implemented
    bundles = db.Column(ARRAY(db.Integer), nullable = False)
    #bundle = db.Column(db.Integer, db.ForeignKey('bundle.bundeId'),nullable = False)
 
    def serialize(self):
           return Serializer.serialize(self)


class Company(db.Model, Serializer):
    '''
    This is the representation of a Company
   '''
 
    __tablename__ = 'company'
    '''
    Representation of a Company in db
    '''
    companyId = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    #bundle = db.Column(db.Integer, db.ForeignKey('bundle.bundeId'),nullable = False)
 
    def serialize(self):
           return Serializer.serialize(self)


class Plugin(db.Model, Serializer):

    '''
    This is the representation as an object and as seen from the DB perspective
    '''
 
    __tablename__ = 'plugin'
    '''
    Representation of a Plugin in the DB
    '''
    pluginId = db.Column(db.Integer, primary_key=True)
    # The pluginID isn't generated in the Class but some other instance, hence the primary key type
    bundleId = db.Column(db.Integer)
    pluginUid = db.Column(UUID, unique=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    shortDescription = db.Column(db.String(250), nullable=False)
    version = db.Column(db.String(250), nullable=False)
    clip = db.Column(ARRAY(db.Integer))
    parameters = db.Column(ARRAY(db.Integer))
    properties = db.Column(JSON)
    tags = db.Column(JSON)
    presets = db.Column(JSON)
    rate = db.Column(db.Integer)
    uri = db.Column(db.String)
    rawIdentifier = db.Column(db.String)
    defautImagePath = db.Column(ARRAY(db.String), nullable=False)
    # Can be empty this it is for user's personnal image sample
    sampleImagePath = db.Column(ARRAY(db.String))
 
    def serialize(self):
           return Serializer.serialize(self)


class Property(db.Model, Serializer):
    '''
    '''
    __tablename__ = "property"
    propertyId = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    paramType = db.Column(db.Integer)
    value = db.Column(ARRAY(db.String))
    readOnly = db.Column(db.Boolean)
    parameterIdF = db.Column(db.Integer, db.ForeignKey('parameter.parameterId'))
    clipIdF = db.Column(db.Integer, db.ForeignKey('clip.clipId'))
 
    def __init__(self, key, isClip):
        if isClip == True : 
            clipIdF = key
        else : 
            parameterIdF = key
 
    def serialize(self):
           return Serializer.serialize(self)


class Clip(db.Model, Serializer):
    '''
    Clip
    '''
    __tablename__ = "clip"
    clipId = db.Column(db.Integer, primary_key = True)
    propertyIdF = db.relationship('Property', backref = 'clip', uselist = False)
 
    def serialize(self):
           return Serializer.serialize(self)


class Parameter(db.Model, Serializer):
    '''
    Parameter
    '''
    __tablename__ = "parameter"
    parameterId = db.Column(db.Integer, primary_key = True)
    propertyIdF = db.relationship('Property', backref = 'parameter', uselist = False)
 
    def serialize(self):
           return Serializer.serialize(self)


db.create_all()
