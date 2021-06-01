from app import app
from flask import render_template, redirect, url_for, request
from database import db, bus_route_database as brd, bus_stops_database as bsd, user_database as ud, \
    conductor_database as cd
from flask_login import current_user
import json


@app.route('/admin_bus_stops')
def admin_bus_stop():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    bus_stop = db.session.query(bsd.BusStops).all()
    return render_template("busstops.html", name=current_user.name, bus_stop=bus_stop)


@app.route('/admin_bus_stops/select/<bus_stop_id>', methods=["GET", "POST"])
def get_admin_bus_stop(bus_stop_id):
    bus_stop: bsd.BusStops = bsd.BusStops.query.filter_by(id=bus_stop_id).first()
    if request.method == 'POST':
        bus_stop.bus_stop = request.form.get('bus_stop')
        bus_stop.longitude = request.form.get('longitude')
        bus_stop.latitude = request.form.get('latitude')
        db.session.commit()
        return {
            "bus_stop": bus_stop.bus_stop,
            "latitude": bus_stop.latitude,
            "longitude": bus_stop.longitude,
        }
    return json.dumps({
        "bus_stop": bus_stop.bus_stop,
        "latitude": bus_stop.latitude,
        "longitude": bus_stop.longitude,
    })
