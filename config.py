from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.mail import Mail
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from os import urandom

app = Flask(__name__)
app.secret_key = urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SchoolWeather2.db'
db = SQLAlchemy(app)
mail = Mail(app)


