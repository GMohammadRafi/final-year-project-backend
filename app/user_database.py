from app import db
from sqlalchemy import ForeignKey


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(300), nullable=False)


class UserOTP(db.Model):
    __tablename__ = 'UserOTP'
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(100), ForeignKey('User.id'))
    sent_to = db.Column(db.String(100), nullable=False)
    expiry_time = db.Column(db.String(150), nullable=False)
    otp = db.Column(db.String(4), nullable=False)


class BookTicket(db.Model):
    __tablename__ = 'BookTicket'
    id = db.Column(db.String(32), primary_key=True)
    booked_user_id = db.Column(db.String(32), primary_key=True)
    bus_no = db.Column(db.String(100), nullable=False)
    starting_bus_stop = db.Column(db.String(100), nullable=False)
    end_bus_stop = db.Column(db.String(100), nullable=False)
    starting_bus_timing = db.Column(db.String(100), nullable=False)
    timings_and_no_of_stop = db.Column(db.String(100), nullable=False)
    face_id = db.Column(db.JSON(), nullable=False)
    payment_states = db.Column(db.Boolean, nullable=False)



class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(100), ForeignKey('User.id'))
    feedback_data = db.Column(db.String(500), nullable=False)
