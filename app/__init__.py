from os import environ, path
from flask import Flask, render_template

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
