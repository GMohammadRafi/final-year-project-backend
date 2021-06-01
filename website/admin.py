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
    bus_stops = db.session.query(bsd.BusStops).all()
    return render_template("busroutes.html", name=current_user.name, bus_routes=bus_routes, bus_stops=bus_stops,
                           bus_stop_id=[bus_s.id for bus_s in bus_stops])


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
