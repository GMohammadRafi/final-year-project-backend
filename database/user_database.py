from database import db
from sqlalchemy import ForeignKey


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(300), nullable=False)
    amount = db.Column(db.Integer, nullable=False)


class UserOTP(db.Model):
    __tablename__ = 'UserOTP'
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(100), ForeignKey('User.id'))
    sent_to = db.Column(db.String(100), nullable=False)
    expiry_time = db.Column(db.String(150), nullable=False)
    otp = db.Column(db.String(4), nullable=False)


class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(100), ForeignKey('User.id'))
    feedback_data = db.Column(db.String(500), nullable=False)
