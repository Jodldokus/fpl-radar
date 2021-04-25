from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ




app = Flask(__name__)
if environ.get('DATABASE_URL') != None:
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL').replace("://", "ql://", 1) or 'sqlite:///myDB.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myDB.db'
app.config['SECRET_KEY'] = 'MEGAsecret'

db = SQLAlchemy(app)

import routes, models

