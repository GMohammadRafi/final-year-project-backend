from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from app import user_database
from app import conductor_database
from app import bus_stops_database
from app import bus_route_database
from app import book_ticket_database

db.create_all()


@app.route('/')
def root():
    return {'Application': 'MY BMTC'}


from app import bus_stops_routes
from app import bus_route_routes
from app import get_bus_no_timings
from app import user_and_conductor_route
from app import user_route
from app import conductor_route
from app import booking_ticket_route
