from app import app, generate_ids as gids, constants as c
from database import book_ticket_database as brd, bus_route_database as busrd, user_database as ud, db, \
    bus_stops_database as busd
from flask import request
from os import path, mkdir
from werkzeug.utils import secure_filename
from difflib import SequenceMatcher
from datetime import datetime
from pytz import timezone
import json

IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG"]
time_zone = timezone('Asia/Kolkata')


@app.route('/book-ticket/face-id', methods=["POST"])
def upload_image():
    url = []
    if request.files:
        target = path.join(c.APP_ROOT, 'images/')
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
    bus_booking_ticket["busFromToDetails"] = json.loads(bus_booking_ticket["busFromToDetails"])
    ticket_id: list = []
    user_data: ud.User = ud.User.query.filter_by(id=bus_booking_ticket['userID']).first()
    if bus_booking_ticket['total_cost'] > user_data.amount:
        return {
                   "message": "No enough amount in your account"
               }, 404
    for bus_detail in bus_booking_ticket["busFromToDetails"]['bus_details']:
        t = set_ticket(bus_detail)
        ticket_id.append(t)
    new_book_ticket = brd.BookedTickets(
        id=gids.generate_id(brd.BookedTickets),
        user_id=user_data.id,
        tickets=ticket_id,
        number_of_tickets=int(bus_booking_ticket['total_ticket']),
        face_id=bus_booking_ticket['images'],
        toatal_time=bus_booking_ticket["busFromToDetails"]['toatal_time'],
        amount_payed=int(bus_booking_ticket['total_cost']),
        booked_date_time=datetime.now(time_zone)
    )
    user_data.amount -= bus_booking_ticket['total_cost']
    db.session.add(new_book_ticket)
    db.session.commit()
    return {
        "message": "Booked Ticket",
    }


@app.route('/get/book-ticket/<user_id>', methods=["POST"])
def get_all_book_ticket(user_id):
    list_result: list = brd.BookedTickets.query.filter_by(user_id=user_id).all()
    if not list_result:
        return {
                   "message": "user do not exist"
               }, 409

    return [{
        "id": result.id,
        "tickets": [get_ticket(ticket_id) for ticket_id in result.tickets],
        "amount_payed": result.amount_payed,
        "booked_date_time": result.booked_date_time,
        "number_of_tickets": result.number_of_tickets,
        "toatal_time": result.toatal_time,
    } for result in list_result]


def set_ticket(bus_details: dict):
    result: busrd.BusRoute = busrd.BusRoute.query.filter_by(
        bus_no=str(bus_details['bus_no']).replace(" ", "").replace("-", "")).first()
    end_bus_stop = bus_details['end_bus_stop']
    starting_bus_stop = bus_details['starting_bus_stop']
    print(f"Starting bus stop(Google): {starting_bus_stop}")
    print(f"Ending bus stop(Google): {end_bus_stop}")
    end_bus_stop_per = []
    starting_bus_stop_per = []
    max_end = 0
    max_end_index = 0
    max_start = 0
    max_start_index = 0
    bus_stop = []
    if result:
        for stop_id in result.list_of_bus_stops:
            bus_stop_data: busd.BusStops = busd.BusStops.query.filter_by(id=stop_id["id"]).first()
            bus_stop.append({"id": bus_stop_data.id, "bus_stop": bus_stop_data.bus_stop})
            end_bus_stop_per.append(SequenceMatcher(None, bus_stop_data.bus_stop, end_bus_stop).ratio())
            starting_bus_stop_per.append(SequenceMatcher(None, bus_stop_data.bus_stop, starting_bus_stop).ratio())
        max_start = max(starting_bus_stop_per)
        max_end = max(end_bus_stop_per)
        max_start_index = starting_bus_stop_per.index(max_start)
        max_end_index = end_bus_stop_per.index(max_end)
        print(f"Max starting value: {max_start}")
        print(f"Max ending value: {max_end}")
        print(f"Starting bus stop(Database): {bus_stop[max_start_index]}")
        print(f"Ending bus stop(Database): {bus_stop[max_end_index]}")
    if max_end > 70 and max_start > 70:
        if max_end_index > max_start_index:
            origin = True
        else:
            origin = False
    else:
        origin = True
    user_data = brd.Ticket(
        id=gids.generate_id(brd.Ticket),
        bus_no=result.id if result else bus_details['bus_no'],
        end_bus_stop=bus_stop[max_end_index]["id"] if max_end > 0.7 else end_bus_stop,
        starting_bus_stop=bus_stop[max_start_index]["id"] if max_start > 0.7 else starting_bus_stop,
        starting_bus_timing=bus_details['starting_bus_timing'],
        timings_and_no_of_stop=bus_details['timings_and_no_of_stop'],
        origin_to_destination=origin
    )
    db.session.add(user_data)
    db.session.commit()
    return user_data.id


def get_ticket(bus_details: str):
    result: brd.Ticket = brd.Ticket.query.filter_by(id=bus_details).first()
    bus_no = result.bus_no
    if not str(result.bus_no).isspace() and len(result.bus_no) == 32:
        tem: busrd.BusRoute = busrd.BusRoute.query.filter_by(id=bus_no).first()
        bus_no = tem.bus_no
    starting_bus_stop = result.starting_bus_stop
    if not str(result.starting_bus_stop).isspace() and len(result.starting_bus_stop) == 32:
        tem: busd.BusStops = busd.BusStops.query.filter_by(id=starting_bus_stop).first()
        starting_bus_stop = tem.bus_stop
    end_bus_stop = result.end_bus_stop
    if not str(result.end_bus_stop).isspace() and len(result.end_bus_stop) == 32:
        tem: busd.BusStops = busd.BusStops.query.filter_by(id=end_bus_stop).first()
        end_bus_stop = tem.bus_stop
    return {
        "id": result.id,
        "bus_no": bus_no,
        "starting_bus_stop": starting_bus_stop,
        "end_bus_stop": end_bus_stop,
        "timings_and_no_of_stop": result.timings_and_no_of_stop,
    }


def allowed_image(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in IMAGE_EXTENSIONS:
        return True
    else:
        return False
