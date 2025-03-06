from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

app = Flask(__name__)

sqlite_url = environ.get("SQLITE_URL")

if not sqlite_url:
    raise ValueError("No SQLITE_URL set for Flask application")

db_path = path.join(basedir, sqlite_url, "myDB.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path

app.config["SECRET_KEY"] = "MEGAsecret"

db = SQLAlchemy(app)

import routes, models
