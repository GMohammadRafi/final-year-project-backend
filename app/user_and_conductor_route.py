from app import app, constants as c, generate_ids as gids
from database import conductor_database as cd, user_database as ud, db

from flask import request

from werkzeug.security import check_password_hash, generate_password_hash
import smtplib
from random import randint
import datetime
import requests


@app.route('/<user_type>/register', methods=["POST"])
def register(user_type):
    if "user" == user_type:
        uid = gids.generate_id(ud.User)
    else:
        uid = request.form.get('id')
    name = request.form.get('name')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    if "user" == user_type:
        result = ud.User.query.filter_by(email=email).first()
    else:
        result = cd.Conductor.query.filter_by(email=email).first()
    if result:
        return {
                   "message": "user already exist"
               }, 409
    else:
        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        if "user" == user_type:
            user_data = ud.User(id=uid,
                                name=name,
                                email=email,
                                phone_number=phone_number,
                                password=hash_and_salted_password,
                                amount=0,
                                )
        else:
            user_data = cd.Conductor(id=uid,
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
            "session_time": c.SESSION_TIME
        }


@app.route('/<user_type>/get-user-details/<user_id>', methods=["GET"])
def get_user_details(user_type, user_id):
    if "user" == user_type:
        result = ud.User.query.filter_by(email=user_id).first()
    else:
        result = cd.Conductor.query.filter_by(email=user_id).first()
    if not result:
        return {
                   "message": "user not exist"
               }, 409
    else:
        return {
            "user_id": result.id,
            "phone_number": result.phone_number,
            "name": result.name,
            "email": result.email,
            "session_time": c.SESSION_TIME
        }


@app.route('/<user_type>/set-user-details/<user_id>', methods=["POST"])
def set_user_details(user_type, user_id):
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    new_password = request.form.get('new_password')
    old_password = request.form.get('old_password')
    if "user" == user_type:
        result = ud.User.query.filter_by(email=user_id).first()
    else:
        result = cd.Conductor.query.filter_by(email=user_id).first()
    if not result:
        return {
                   "message": "user do not exist"
               }, 409
    if name is not None or phone_number is not None:
        result.name = name if name is not None else result.name
        result.phone_number = phone_number if phone_number is not None else result.phone_number
    if old_password is not None and new_password is not None:
        if check_password_hash(result.password, old_password):
            hash_and_salted_password = generate_password_hash(
                new_password,
                method='pbkdf2:sha256',
                salt_length=8
            )
            result.password = hash_and_salted_password
        else:
            return {
                       "message": "Entered Password is wrong"
                   }, 403
    db.session.commit()
    return {
        "user_id": result.id,
        "phone_number": result.phone_number,
        "name": result.name,
        "email": result.email,
        "session_time": c.SESSION_TIME
    }


@app.route('/<user_type>/is-user/<user_id>', methods=["GET"])
def login(user_type, user_id):
    if "user" == user_type:
        result = ud.User.query.filter_by(id=user_id).first()
    else:
        result = cd.Conductor.query.filter_by(id=user_id).first()
    if not result:
        return {
                   "message": "User Do Not Exist"
               }, 403
    else:
        return {
            "message": "User Do Exist"
        }


@app.route('/<user_type>/login', methods=["POST"])
def login(user_type):
    email = request.form.get('email')
    password = request.form.get('password')
    if "user" == user_type:
        result = ud.User.query.filter_by(email=email).first()
    else:
        result = cd.Conductor.query.filter_by(email=email).first()
    if not result:
        return {
                   "message": "User Do Not Exist"
               }, 403
    elif check_password_hash(result.password, password):
        return {
            "user_id": result.id,
            "phone_number": result.phone_number,
            "name": result.name,
            "email": result.email,
            "session_time": c.SESSION_TIME
        }
    else:
        return {
                   "message": "Entered Password is wrong"
               }, 403


@app.route('/<user_type>/send-otp', methods=["POST"])
def send_otp(user_type):
    user_data = request.form.get('user_data')
    if user_data.isnumeric():
        #     phone number
        if "user" == user_type:
            result = ud.User.query.filter_by(phone_number=str(user_data)).first()
        else:
            result = cd.Conductor.query.filter_by(phone_number=str(user_data)).first()
        if not result:
            return {
                       "message": "user do not exist or phone number entered is wrong the phone number should be only "
                                  "10 digit "
                   }, 403
        else:
            return sending_sms(user_type, user_details=result)
    else:
        # mail id
        if "user" == user_type:
            result = ud.User.query.filter_by(email=user_data).first()
        else:
            result = cd.Conductor.query.filter_by(email=user_data).first()
        if not result:
            return {
                       "message": "user do not exist because email or phone number entered is wrong, \n if phone "
                                  "number is entered then it should be only 10 digit"
                   }, 403
        else:
            return sending_mail(user_type, user_details=result)


@app.route('/<user_type>/resend-otp', methods=["POST"])
def resend_otp(user_type):
    otp_id = request.form.get('otp_id')
    sent_to = request.form.get('through')
    if "user" == user_type:
        result = ud.UserOTP.query.filter_by(id=otp_id).first()
    else:
        result = cd.ConductorOTP.query.filter_by(id=otp_id).first()
    if sent_to == 'mail':
        return sending_mail(user_type, otp_user_data=result)
    else:
        return sending_sms(user_type, otp_user_data=result)


@app.route('/<user_type>/verify-otp', methods=["POST"])
def verify_otp(user_type):
    otp_id = request.form.get('otp_id')
    otp = request.form.get('otp')
    if "user" == user_type:
        otp_data = ud.UserOTP.query.filter_by(id=otp_id).first()
        user_data = ud.User.query.filter_by(id=otp_data.user_id).first()
    else:
        otp_data = cd.ConductorOTP.query.filter_by(id=otp_id).first()
        user_data = cd.Conductor.query.filter_by(id=otp_data.user_id).first()
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
                       "message": "Please enter a proper OTP"
                   }, 403
    else:
        sending_mail(otp_user_data=otp_data)
        return {
                   "message": "Time Expired Resend The OTP"
               }, 410


@app.route('/<user_type>/change-password', methods=["POST"])
def change_password(user_type):
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    if "user" == user_type:
        result = ud.User.query.filter_by(id=user_id).first()
    else:
        result = cd.Conductor.query.filter_by(id=user_id).first()
    if not result:
        return {
                   "message": "User Does not Exist"
               }, 303
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


def sending_mail(user_type, otp_user_data=None, user_details=None):
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
        user_id = user_details.id
        email = user_details.email
        if "user" == user_type:
            uid = gids.generate_id(ud.UserOTP)
            otp_user_data = ud.UserOTP(id=uid,
                                       sent_to=user_details.email,
                                       expiry_time=str(future_time),
                                       user_id=user_id,
                                       otp=str(otp)
                                       )
        else:
            uid = gids.generate_id(cd.ConductorOTP)
            otp_user_data = cd.ConductorOTP(id=uid,
                                            sent_to=user_details.email,
                                            expiry_time=str(future_time),
                                            user_id=user_id,
                                            otp=str(otp)
                                            )
        db.session.add(otp_user_data)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
        connection.login(user=c.SENDER_EMAIL, password=c.SENDER_PASSWORD)
        sub = 'OTP Verification for MY BMTC APP'
        body = f'Your OTP pin code is displayed below:\nYour  OTP will be expired in 10 minutes \n  Your OTP is {otp} '
        meg = f'Subject: {sub}\n\n{body}'
        connection.sendmail(c.SENDER_EMAIL, email, meg)
        status_code, _ = connection.noop()
        if 100 < status_code < 300:
            db.session.commit()
        else:
            return {
                       "message": "Something Went Wrong!"
                   }, 501
    return {
        "otp_id": uid,
        "sent_to": str(email),
        "through": "mail"
    }


def sending_sms(user_type, otp_user_data=None, user_details: ud.User = None):
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
        user_id = user_details.id
        phone_number = user_details.phone_number
        if "user" == user_type:
            uid = gids.generate_id(ud.UserOTP)
            otp_user_data = ud.UserOTP(id=uid,
                                       sent_to=str(phone_number),
                                       expiry_time=str(future_time),
                                       user_id=user_id,
                                       otp=str(otp)
                                       )
        else:
            uid = gids.generate_id(cd.ConductorOTP)
            otp_user_data = cd.ConductorOTP(id=uid,
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
        'authorization': c.SMS_API_KEY,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
    }
    response = requests.request("POST", c.SMS_URL, data=payload, headers=headers)
    if 100 < response.status_code < 300:
        db.session.commit()
    else:
        return {
                   "message": "Something Went Wrong!"
               }, 501
    return {
        "otp_id": uid,
        "sent_to": str(phone_number),
        "through": "sms"
    }
