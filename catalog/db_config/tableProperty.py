from flask import Flask
import psycopg2

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, BYTEA

app = Flask(__name__)

# ADD
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://webopenfx:tuttle@localhost:5432/webopenfx_db"

db = SQLAlchemy(app)

properties = db.Table('property',
    db.Column('id', db.Integer, primary_key = True),
    db.Column('paramId', db.Integer, db.ForeignKey('parameter.id', use_alter=True, name='fk_bundle_param_id')),
    db.Column('clipId', db.Integer, db.ForeignKey('clip.id', use_alter=True, name='fk_bundle_clip_id')),
    db.Column('name', db.String, nullable=False),
    db.Column('type', db.String, nullable=False),
    db.Column('defaultValue', BYTEA, nullable=False),
)

db.create_all()
db.session.commit()
