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

bundle = db.Table('bundle',
    db.Column('id', db.Integer, primary_key = True),
    db.Column('bundleId', UUID),
    db.Column('userId', db.Integer, db.ForeignKey('user.id', use_alter=True, name='fk_bundle_user_id')),
    db.Column('companyId', db.Integer, db.ForeignKey('company.id', use_alter=True, name='fk_bundle_company_id')),
    db.Column('name', db.String, nullable=False),
    db.Column('description', db.String, nullable=False),
    db.Column('uploadDate', db.DateTime, nullable=False),
    db.Column('shared', db.Boolean, nullable=False),
    db.Column('contributors', ARRAY(db.Integer)),
    db.Column('architecture', ARRAY(db.String), nullable=False),
    db.Column('plugins', ARRAY(db.Integer), nullable=False)
    db.Column('uploadDate', db.Boolean, nullable=False)
)

db.create_all()
db.session.commit()
