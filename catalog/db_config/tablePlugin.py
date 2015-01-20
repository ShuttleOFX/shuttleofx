from flask import Flask
import psycopg2

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, ARRAY , JSON

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://webopenfx:tuttle@localhost:5432/webopenfx_db"
db = SQLAlchemy(app)

plugin = db.Table('plugin2',
    db.Column('id', db.Integer, primary_key = True, autoincrement = True),
    db.Column('pluginID', UUID, unique = True),
    db.Column('name',db.String,nullable=False),
    db.Column('description', db.String, nullable=False),
    db.Column('shortDescription', db.String, nullable=False),
    db.Column('version', db.String, nullable=False),
    db.Column('clip', JSON),
    db.Column('parameters', JSON, nullable=False),
    db.Column('properties', JSON, nullable=False),
    db.Column('tags', JSON),
    db.Column('presets', JSON),
    db.Column('rate', db.Integer),
    db.Column('defautImagePath', ARRAY(db.String), nullable=False),
    db.Column('sampleImagePath', ARRAY(db.String))
)

db.create_all()
db.session.commit()
