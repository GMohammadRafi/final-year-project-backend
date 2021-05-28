from app import app, generate_ids as gids, user_database as ud, book_ticket_database as brd, bus_route_database as busd, \
    db
from flask import request
from os import path, mkdir
from werkzeug.utils import secure_filename
import json

APP_ROOT = path.dirname(path.abspath(__file__))
IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG"]


@app.route('/book-ticket/face-id', methods=["POST"])
def upload_image():
    url = []
    if request.files:
        target = path.join(APP_ROOT, 'images/')
        if not path.isdir(target):
            mkdir(target)
        file = request.files.get("images")
        if file.filename == "":
            return {
                       "message": "No filename"
                   }, 400
        if not allowed_image(file.filename):
            return {
                       "message": "file is not allowed"
                   }, 400
        filename = secure_filename(file.filename)
        if not path.isfile(path.join(target, filename)):
            url.append(filename)
        else:
            return {
                       "message": "File already exist"
                   }, 400

        filename = secure_filename(file.filename)
        file.save(path.join(target, filename))
    return {
        "photos_url": url[0]
    }


@app.route('/book-ticket', methods=["POST"])
def book_ticket():
    bus_booking_ticket: dict = json.loads(request.data)
    ticket_id = []
    for bus_detail in bus_booking_ticket['bus_details']:
        ticket_id.append(ticket(bus_detail))
    user_data: ud.User = ud.User.query.filter_by(id=bus_booking_ticket['user_id']).first()
    if bus_booking_ticket['amount'] > user_data.amount:
        return {
                   "message": "No enough amount in your account"
               }, 404
    user_data.amount -= bus_booking_ticket['amount']
    new_book_ticket = brd.BookedTickets(
        id=gids.generate_id(brd.BookedTickets),
        user_id=user_data.id,
        tickets=ticket_id,
        face_id=bus_booking_ticket['face_id'],
        toatal_time=bus_booking_ticket['toatal_time'],
        amount_payed=bus_booking_ticket['amount']
    )
    db.session.add(new_book_ticket)
    db.session.commit()
    return {
        "message": "Booked Ticket",
    }


def ticket(bus_details: dict):
    result: busd.BusRoute = busd.BusRoute.query.filter_by(bus_no=bus_details['bus_no']).first()
    user_data = brd.Ticket(
        id=gids.generate_id(brd.Ticket),
        bus_no=result.id if result else bus_details['bus_no'],
        starting_bus_stop=bus_details['starting_bus_timing'],
        end_bus_stop=bus_details['starting_bus_stop'],
        starting_bus_timing=bus_details['starting_bus_timing'],
        timings_and_no_of_stop=bus_details['timings_and_no_of_stop'],
    )
    db.session.add(user_data)
    db.session.commit()
    return id


def allowed_image(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in IMAGE_EXTENSIONS:
        return True
    else:
        return False
