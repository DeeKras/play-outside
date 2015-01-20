from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask.ext.heroku import Heroku

from os import urandom, environ



app = Flask(__name__)
app.secret_key = urandom(32)

engine = create_engine("postgresql+psycopg2://SchoolWeather.db")

heroku = Heroku()
heroku.init_app(app)

# SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', 'sqlite:///SchoolWeather2.db')
db = SQLAlchemy(app)




# db.create_all(engine)
# db.text_factory = str


