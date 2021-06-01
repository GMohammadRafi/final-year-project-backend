from app import app
from flask import render_template, redirect, url_for
from database import db, bus_route_database as brd, bus_stops_database as bsd, user_database as ud, \
    conductor_database as cd
from flask_login import current_user


@app.route('/admin_bus_routes')
def admin_bus_routes():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    bus_routes = db.session.query(brd.BusRoute).all()
    bus_stops = db.session.query(bsd.BusStops).all()
    return render_template("busroutes.html", name=current_user.name, bus_routes=bus_routes, bus_stops=bus_stops,
                           bus_stop_id=[bus_s.id for bus_s in bus_stops])
