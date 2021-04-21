from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from app import user_database
from app import conductor_database

db.create_all()


@app.route('/')
def root():
    return {'Application': 'MY BMTC'}


from app import user_and_conductor_route
from app import user_route
from app import conductor_route
