from app import app
from flask import render_template, redirect, url_for
from database import db, bus_route_database as brd, bus_stops_database as bsd, user_database as ud, \
    conductor_database as cd
from flask_login import current_user


@app.route('/admin_dashboard')
def admin_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    return render_template("dashboard.html", name=current_user.name, details={
        "bus_routes": db.session.query(brd.BusRoute).count(),
        "bus_stops": db.session.query(bsd.BusStops).count(),
        "users": db.session.query(ud.User).count(),
        "conductor": db.session.query(cd.Conductor).count(),
    })


@app.route('/admin_conductor')
def admin_conductor():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    return render_template("conductor.html", name=current_user.name)


@app.route('/admin_customer')
def admin_customer():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    return render_template("customer.html", name=current_user.name)


@app.route('/admin_bus_stops')
def admin_bus_stop():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    bus_stop = db.session.query(bsd.BusStops).all()
    return render_template("busstops.html", name=current_user.name, bus_stop=bus_stop)


@app.route('/admin_bus_routes')
def admin_bus_routes():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    bus_routes = db.session.query(brd.BusRoute).all()
    route: brd.BusRoute
    return_list = []
    for route in bus_routes:
        bus_route_temp = {"bus_no": route.bus_no, "distance": route.distance}
        temp = []
        for bus_stop_details in route.list_of_bus_stops:
            result: bsd.BusStops
            result = bsd.BusStops.query.filter_by(id=bus_stop_details["id"]).first()
            temp.append(result.bus_stop)
        bus_route_temp["list_of_bus_stops"] = temp
        return_list.append(bus_route_temp)
    return render_template("busroutes.html", name=current_user.name, bus_routes=return_list)


@app.route('/admin_booked_ticket')
def admin_booked_ticket():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    return render_template("bookedticket.html", name=current_user.name)


@app.route('/admin_feedback')
def admin_feedback():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    return render_template("feedback.html", name=current_user.name)
