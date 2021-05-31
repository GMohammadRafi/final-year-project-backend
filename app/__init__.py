from os import environ
from flask import Flask
from flask_login import LoginManager


app = Flask('__name__')
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)

import database

database.db.create_all()


from app import bus_stops_routes
from app import bus_route_routes
from app import get_bus_no_timings
from app import user_and_conductor_route
from app import user_route
from app import conductor_route
from app import booking_ticket_route
import website
