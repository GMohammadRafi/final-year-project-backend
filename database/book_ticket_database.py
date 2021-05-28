from database import db
from sqlalchemy import ForeignKey

class Ticket(db.Model):
    __tablename__ = 'Ticket'
    id = db.Column(db.String(32), primary_key=True)
    bus_no = db.Column(db.String(32), nullable=False)
    starting_bus_stop = db.Column(db.String(100), nullable=False)
    end_bus_stop = db.Column(db.String(100), nullable=False)
    starting_bus_timing = db.Column(db.String(100), nullable=False)
    timings_and_no_of_stop = db.Column(db.String(100), nullable=False)


class BookedTickets(db.Model):
    __tablename__ = 'BookedTickets'
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(32), ForeignKey('User.id'))
    tickets = db.Column(db.JSON(), nullable=False)
    face_id = db.Column(db.JSON(), nullable=False)
    toatal_time = db.Column(db.String(100), nullable=False)
    amount_payed = db.Column(db.Boolean, nullable=False)
