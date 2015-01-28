import os
from flask import Flask


app = Flask(__name__)


import client.views
import client.plugins
import client.upload
import client.demo

