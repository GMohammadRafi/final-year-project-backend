from database import db
from flask_login import UserMixin


class Admin(UserMixin, db.Model):
    __tablename__ = 'Admin'
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
