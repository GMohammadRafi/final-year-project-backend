from database import db
from sqlalchemy import ForeignKey


class Conductor(db.Model):
    __tablename__ = 'Conductor'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(300), nullable=False)


class ConductorOTP(db.Model):
    __tablename__ = 'ConductorOTP'
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(100), ForeignKey('Conductor.id'))
    sent_to = db.Column(db.String(100), nullable=False)
    expiry_time = db.Column(db.String(150), nullable=False)
    otp = db.Column(db.String(4), nullable=False)
