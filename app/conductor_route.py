from app import app, generate_ids as gids, constants  as c
from os import path, listdir
from flask import request
from database import db, conductor_database as cd, bus_route_database as brd, bus_stops_database as bsd, \
    book_ticket_database as btd
from datetime import datetime
from sqlalchemy import or_
from pytz import timezone

time_zone = timezone('Asia/Kolkata')


@app.route('/conductor/set/current-running-bus', methods=["POST"])
def current_running_bus():
    conductor_id = request.form.get('conductor_id')
    bus_route_id = request.form.get('bus_route_id')
    through_loc = request.form.get('through_loc')
    result = cd.RunningBuses.query.filter_by(conductor_id=conductor_id).all()
    if result:
        r: cd.RunningBuses
        for r in result:
            r.status = False
    new_running_bus = cd.RunningBuses(id=gids.generate_id(cd.RunningBuses),
                                      conductor_id=conductor_id,
                                      bus_route_id=bus_route_id,
                                      through_loc=bool(int(through_loc)),
                                      status=True,
                                      start_of_trip=datetime.now(time_zone)
                                      )

    db.session.add(new_running_bus)
    db.session.commit()
    return {
        "id": new_running_bus.id, "conductor_id": conductor_id, "bus_route_id": bus_route_id, "through_loc": through_loc
    }


@app.route('/conductor/set/live-location/<conductor_id>', methods=["POST", "PATCH"])
def set_current_running_bus(conductor_id):
    through = bool(int(request.form.get('through')))
    if request.method == 'PATCH':
        r: cd.RunningBuses = cd.RunningBuses.query.filter_by(conductor_id=conductor_id, end_of_trip=None).first()
        r.end_of_trip = datetime.now(time_zone)
        result: cd.CurrentPosition = cd.CurrentPosition.query.filter_by(conductor_id=conductor_id).first()
        number_of_persons = setting_bus_stop_passed(result.bus_route_id, result.passed_bus_stop_id, through)
        db.session.delete(result)
        db.session.commit()

        return {"message": "Trip Completed", "number_of_persons": number_of_persons}

    bus_route_id = request.form.get('bus_route_id')
    passed_bus_stop_id = request.form.get('passed_bus_stop_id')
    next_bus_stop_id = request.form.get('next_bus_stop_id')

    result: cd.CurrentPosition = cd.CurrentPosition.query.filter_by(conductor_id=conductor_id).first()
    if result:
        result.bus_route_id = bus_route_id
        result.passed_bus_stop_id = passed_bus_stop_id
        result.next_bus_stop_id = next_bus_stop_id
        db.session.commit()
    else:
        result = cd.CurrentPosition(id=gids.generate_id(cd.RunningBuses),
                                    conductor_id=conductor_id,
                                    bus_route_id=bus_route_id,
                                    passed_bus_stop_id=passed_bus_stop_id,
                                    next_bus_stop_id=next_bus_stop_id,
                                    )
        db.session.add(result)
        db.session.commit()
    number_of_persons = setting_bus_stop_passed(result.bus_route_id, result.passed_bus_stop_id, through)
    return {
        "id": result.id,
        "bus_route_id": bus_route_id,
        "passed_bus_stop_id": passed_bus_stop_id,
        "next_bus_stop_id": next_bus_stop_id,
        "number_of_persons": number_of_persons
    }


@app.route('/live-location/<bus_id>', methods=["GET"])
def live_location(bus_id):
    bus_running = cd.CurrentPosition.query.filter_by(bus_route_id=bus_id).all()
    result = []
    b: cd.CurrentPosition
    for b in bus_running:
        result.append({
            "passed": b.passed_bus_stop_id,
            "next": b.next_bus_stop_id
        })
    return {
        "active": result
    }


@app.route('/get/trip/<user_id>', methods=["GET"])
def get_all_trip(user_id):
    list_result: list = cd.RunningBuses.query.filter_by(conductor_id=user_id, status=False).all()
    result: cd.RunningBuses
    if not list_result:
        return {
                   "message": "No Trips"
               }, 409
    to_send = []
    for result in list_result:
        temp_bus_rout: brd.BusRoute = brd.BusRoute.query.filter_by(id=result.bus_route_id).first()
        stop1 = bsd.BusStops.query.filter_by(id=temp_bus_rout.list_of_bus_stops[0]["id"]).first().bus_stop
        stop2 = bsd.BusStops.query.filter_by(
            id=temp_bus_rout.list_of_bus_stops[len(temp_bus_rout.list_of_bus_stops) - 1]["id"]).first().bus_stop
        to_send.append({
            "id": result.id,
            "bus_route_no": temp_bus_rout.bus_no,
            "start_of_trip": result.start_of_trip,
            "starting_stop": stop2 if result.through_loc else stop1,
            "ending_stop": stop1 if result.through_loc else stop2,
            "end_of_trip": result.end_of_trip,
        })

    return {"trips": to_send}


@app.route('/get/all-unbooked-users/<user_id>', methods=["GET"])
def get_all_unbooked_user(user_id):
    list_images = listdir(path.join(c.APP_ROOT, "images"))
    result = []
    for i in list_images:
        if i.startswith(user_id):
            result.append(i)
    return {"images": result}


def setting_bus_stop_passed(bus_route_id, passed_bus_stop_id, through):
    count = 0
    tickets = btd.Ticket.query.filter_by(
        bus_no=bus_route_id,
        end_bus_stop=passed_bus_stop_id,
        origin_to_destination=through,
        status=0
    ).all()
    t: btd.Ticket
    for t in tickets:
        t.status = 2

    tickets = btd.Ticket.query.filter_by(
        bus_no=bus_route_id,
        end_bus_stop=passed_bus_stop_id,
        origin_to_destination=through,
        status=4
    ).all()
    for t in tickets:
        t.status = 3
        count += 1

    conductor_tickets = btd.TicketsBookedByConductor.query.filter_by(
        bus_no_id=bus_route_id,
        end_bus_id=passed_bus_stop_id,
        status=4,
    ).all()
    ct: btd.TicketsBookedByConductor
    for ct in conductor_tickets:
        ct.status = 3
        count += 1
    db.session.commit()
    return count


@app.route('/get/all-booked-tickets/<conductor_id>', methods=["GET"])
def all_booked_tickets(conductor_id):
    tickets_by_conductor = []
    tickets_by_user = []
    try:
        current_bus_running: cd.RunningBuses = cd.RunningBuses.query.filter_by(conductor_id=conductor_id,
                                                                               status=True).first()
        tickets_booked_by_conductor = btd.TicketsBookedByConductor.query.filter_by(conductor_id=conductor_id,
                                                                                   status=4).all()
        booked_tickets = db.session.query(btd.BookedTickets).all()
        tickets_booked_by_users = btd.Ticket.query.filter(btd.Ticket.bus_no == current_bus_running.bus_route_id,
                                                          or_(btd.Ticket.status == 4, btd.Ticket.status == 0),
                                                          btd.Ticket.origin_to_destination == current_bus_running.through_loc).all()

        tdc: btd.TicketsBookedByConductor
        for tdc in tickets_booked_by_conductor:
            tickets_by_conductor.append(
                {
                    "id": tdc.id,
                    "number_of_tickets": tdc.number_of_tickets,
                    "starting_bus_id": bsd.BusStops.query.filter_by(id=tdc.starting_bus_id).first().bus_stop,
                    "end_bus_id": bsd.BusStops.query.filter_by(id=tdc.end_bus_id).first().bus_stop,
                    "phone_number": tdc.phone_number,
                    "amount_payed": tdc.amount_payed,
                }
            )

        tdu: btd.Ticket
        for tdu in tickets_booked_by_users:
            b: btd.BookedTickets
            for b in booked_tickets:
                if tdu.id in b.tickets:
                    print(tdu.starting_bus_stop)
                    tickets_by_user.append({
                        "id": tdu.id,
                        "starting_bus_stop": bsd.BusStops.query.filter_by(id=tdu.starting_bus_stop).first().bus_stop,
                        "end_bus_stop": bsd.BusStops.query.filter_by(id=tdu.end_bus_stop).first().bus_stop,
                        "status": tdu.status,
                        "number_of_tickets": b.number_of_tickets,
                        "face_id": b.face_id,
                    })
                    break
    except:
        return {
            "message": "Something went wrong!"
        }, 300
    return {
        "tickets_by_conductor": tickets_by_conductor,
        "tickets_by_user": tickets_by_user,
    }
