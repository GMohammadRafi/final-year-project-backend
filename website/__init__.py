from app import app, login_manager
from database import admin_database as ad, db, bus_route_database as brd, bus_stops_database as bsd, \
    user_database as ud, conductor_database as cd
from werkzeug.security import check_password_hash
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user


@login_manager.user_loader
def load_user(user_id):
    return ad.Admin.query.get(user_id)


@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = ad.Admin.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('admin_login'))
        elif not not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('admin_login'))
        else:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
    return render_template("admin_login.html", logged_in=current_user.is_authenticated)


@app.route('/admin_logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('root'))


@app.route('/')
def root():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    return render_template("index.html")


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
    return render_template("busstops.html", name=current_user.name)


@app.route('/admin_bus_routes')
def admin_bus_routes():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    return render_template("busroutes.html", name=current_user.name)


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
