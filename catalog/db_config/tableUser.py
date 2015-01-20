from flask import Flask
import psycopg2
import uuid
from datetime import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON


app = Flask(__name__)

# ADD
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://webopenfx:tuttle@localhost:5432/webopenfx_db"

db = SQLAlchemy(app)

user = db.Table('user',
    db.Column('id', db.Integer, primary_key = True),
    db.Column('name', db.String, nullable=False),
    db.Column('firstname', db.String, nullable=False),
    db.Column('mail', db.String, nullable=False),
    db.Column('company', ARRAY(db.Integer)),
    db.Column('bundle', ARRAY(db.Integer)),

)

db.create_all()
db.session.commit()
