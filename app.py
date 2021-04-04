from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlit:///myDB.db'
app.config['SECRET_KEY'] = 'MEGAsecret'

db = SQLAlchemy(app)

import routes

