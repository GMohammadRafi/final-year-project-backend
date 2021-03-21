import uuid
from os import environ
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from werkzeug.security import check_password_hash, generate_password_hash
import smtplib
from random import randint
import datetime
import requests

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(300), nullable=False)


class OTP(db.Model):
    __tablename__ = 'OTP'
    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.String(100), ForeignKey('User.id'))
    sent_to = db.Column(db.String(100), nullable=False)
    expiry_time = db.Column(db.String(150), nullable=False)
    otp = db.Column(db.String(4), nullable=False)


SENDER_EMAIL = environ.get('SENDER_EMAIL')
SENDER_PASSWORD = environ.get('SENDER_PASSWORD')
SMS_API_KEY = environ.get('SMS_API_KEY')
SMS_URL = environ.get('SMS_URL')

db.create_all()

SESSION_TIME = 10 * 24 * 60 * 60


def generate_id(table_data: db.Model):
    uid = str(uuid.uuid4()).replace('-', '')
    result = table_data.query.filter_by(id=uid).first()
    if not result:
        return uid
    else:
        generate_id(table_data)


@app.route('/user/login', methods=["POST"])
def login():
    args = {
        "email": request.form.get('email'),
        "password": request.form.get('password')
    }
    result = User.query.filter_by(email=args['email']).first()
    if not result:
        return {
            "error": 300,
            "message": "user do not exist"
        }
    elif check_password_hash(result.password, args['password']):
        return {
            "user_id": result.id,
            "phone_number": result.phone_number,
            "name": result.name,
            "email": result.email,
            "session_time": SESSION_TIME
        }
    else:
        return {
            "error": 300,
            "message": "Entered Password is wrong"
        }


@app.route('/')
def root():
    return {'Application': 'MY BMTC'}


@app.route('/user/register', methods=["POST"])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    result = User.query.filter_by(email=email).first()
    if result:
        return {
            "error": 300,
            "message": "user already exist"
        }
    else:
        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        uid = generate_id(User)
        user_data = User(id=uid,
                         name=name,
                         email=email,
                         phone_number=phone_number,
                         password=hash_and_salted_password,
                         )
        db.session.add(user_data)
        db.session.commit()
        return {
            "user_id": uid,
            "phone_number": phone_number,
            "name": name,
            "email": email,
            "session_time": SESSION_TIME
        }


@app.route('/user/send-otp', methods=["POST"])
def send_otp():
    user_data = request.form.get('user_data')
    if user_data.isnumeric():
        #     phone number
        result = User.query.filter_by(phone_number=str(user_data)).first()
        if not result:
            return {
                "error": 300,
                "message": "user do not exist or phone number entered is wrong the phone number should be only 10 digit"
            }
        else:
            return sending_sms(user_details=result)
    else:
        # mail id
        result = User.query.filter_by(email=user_data).first()
        if not result:
            return {
                "error": 300,
                "message": "user do not exist because email or phone number entered is wrong, \n if phone number is "
                           "entered then it should be only 10 digit"
            }
        else:
            return sending_mail(user_details=result)


@app.route('/user/resend-otp', methods=["POST"])
def resend_otp():
    otp_id = request.form.get('otp_id')
    sent_to = request.form.get('sent_to')
    result = OTP.query.filter_by(id=otp_id).first()
    if sent_to == 'mail':
        return sending_mail(otp_user_data=result)
    else:
        return sending_sms(otp_user_data=result)


@app.route('/user/verify-otp', methods=["POST"])
def verify_otp():
    otp_id = request.form.get('otp_id')
    otp = request.form.get('otp')
    otp_data: OTP = OTP.query.filter_by(id=otp_id).first()
    user_data: User = User.query.filter_by(id=otp_data.user_id).first()
    current_time = datetime.datetime.now()
    if str(current_time) < otp_data.expiry_time:
        if str(otp) == otp_data.otp:
            db.session.delete(otp_data)
            db.session.commit()
            return {
                "user_id": otp_data.user_id,
                "user_name": user_data.name
            }
        else:
            return {
                "error": 300,
                "message": "Please enter a proper OTP"
            }
    else:
        sending_mail(otp_user_data=otp_data)
        return {
            "error": 300,
            "message": "Time Expired Resend The OTP"
        }


@app.route('/user/change-password', methods=["POST"])
def change_password():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    result: User = User.query.filter_by(id=user_id).first()
    if not result:
        return {
            "error": 300,
            "message": "User Does not Exist"
        }
    else:
        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        result.password = hash_and_salted_password
        db.session.commit()
        return {
            "message": "Password Changed Successfully"
        }


def sending_mail(otp_user_data=None, user_details=None):
    otp = randint(1111, 9999)
    current_time = datetime.datetime.now()
    ten_min = datetime.timedelta(minutes=10)
    future_time = current_time + ten_min
    if otp_user_data:
        uid = otp_user_data.id
        email = otp_user_data.sent_to
        otp_user_data.otp = str(otp)
        otp_user_data.expiry_time = str(future_time)
    else:
        uid = generate_id(OTP)
        user_id = user_details.id
        email = user_details.email
        otp_user_data = OTP(id=uid,
                            sent_to=user_details.email,
                            expiry_time=str(future_time),
                            user_id=user_id,
                            otp=str(otp)
                            )
        db.session.add(otp_user_data)
    db.session.commit()

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.ehlo()
        connection.starttls()
        connection.ehlo()

        connection.login(user=SENDER_EMAIL, password=SENDER_PASSWORD)
        sub = 'OTP Verification for MY BMTC APP'
        body = f'Your OTP pin code is displayed below:\nYour  OTP will be expired in 10 minutes \n  Your OTP is {otp} '
        meg = f'Subject: {sub}\n\n{body}'
        connection.sendmail(SENDER_EMAIL, email, meg)
        status_code, _ = connection.noop()
        print(connection.noop())
        if 100 > status_code < 300:
            db.session.commit()
        else:
            return {
                "error": 300,
                "message": "Something Went Wrong!"
            }
    return {
        "otp_id": uid,
        "sent_to": "mail"
    }


def sending_sms(otp_user_data: OTP = None, user_details: User = None):
    otp = randint(1111, 9999)
    current_time = datetime.datetime.now()
    ten_min = datetime.timedelta(minutes=10)
    future_time = current_time + ten_min
    if otp_user_data:
        uid = otp_user_data.id
        phone_number = otp_user_data.sent_to
        otp_user_data.otp = str(otp)
        otp_user_data.expiry_time = str(future_time)
    else:
        uid = generate_id(OTP)
        user_id = user_details.id
        phone_number = user_details.phone_number
        otp_user_data = OTP(id=uid,
                            sent_to=str(phone_number),
                            expiry_time=str(future_time),
                            user_id=user_id,
                            otp=str(otp)
                            )
        db.session.add(otp_user_data)

    sub = 'OTP Verification for MY BMTC APP'
    body = f'Your OTP pin code is displayed below:\nYour  OTP will be expired in 10 minutes \n  Your OTP is {otp} '
    meg = f'Subject: {sub}\n\n{body}'
    payload = f"sender_id=FSTSMS&message={meg}&language=english&route=p&numbers={phone_number}"

    headers = {
        'authorization': SMS_API_KEY,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
    }
    response = requests.request("POST", SMS_URL, data=payload, headers=headers)
    print(response.status_code)
    if 100 < response.status_code < 300:
        db.session.commit()
    else:
        return {
            "error": 300,
            "message": "Something Went Wrong!"
        }
    return {
        "otp_id": uid,
        "sent_to": "sms"
    }


if __name__ == "__main__":
    app.run()
