from flask import Flask
import psycopg2

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, BYTEA

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://webopenfx:tuttle@localhost:5432/webopenfx_db"

db = SQLAlchemy(app)

parameter = db.Table('paramater',
    db.Column('id', db.Integer, primary_key = True),
    db.Column('name', db.String, nullable = False),
    db.Column('type', db.Integer, primary_key = True),
    db.Column('value', ARRAY(db.String), primary_key = True),
    db.Column('readOnly', db.Boolean, primary_key = True),
)

db.create_all()
db.session.commit()
