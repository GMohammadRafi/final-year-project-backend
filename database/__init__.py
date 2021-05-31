from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

from database import user_database
from database import conductor_database
from database import bus_stops_database
from database import bus_route_database
from database import book_ticket_database
from database import admin_database
