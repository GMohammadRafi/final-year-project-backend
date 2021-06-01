from app import app
from flask import render_template, redirect, url_for, request
from database import db, bus_route_database as brd, bus_stops_database as bsd, user_database as ud, \
    conductor_database as cd, book_ticket_database as btd
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
    conductor = db.session.query(cd.Conductor).all()
    return render_template("conductor.html", name=current_user.name, conductor=conductor)


@app.route('/admin_conductor/delete/<admin_conductor_id>', methods=["DELETE"])
def delete_admin_conductor(admin_conductor_id: str):
    admin_c: cd.Conductor = cd.Conductor.query.filter_by(id=admin_conductor_id).first()
    db.session.delete(admin_c)
    db.session.commit()
    return {
        "message": "deleted"
    }


@app.route('/admin_customer')
def admin_customer():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    user = db.session.query(ud.User).all()
    return render_template("customer.html", name=current_user.name, user=user)


@app.route('/admin_customer/delete/<admin_customer_id>', methods=["DELETE"])
def delete_admin_customer(admin_customer_id: str):
    admin_c: ud.User = ud.User.query.filter_by(id=admin_customer_id).first()
    db.session.delete(admin_c)
    db.session.commit()
    return {
        "message": "deleted"
    }


@app.route('/admin_booked_ticket')
def admin_booked_ticket():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    list_result = db.session.query(btd.BookedTickets).all()
    return render_template("bookedticket.html", name=current_user.name, bookedtickets=[
        {
            "user_name": ud.User.query.filter_by(id=result.user_id).first().name,
            "tickets": [get_ticket(ticket_id) for ticket_id in result.tickets],
            "amount_payed": result.amount_payed,
            "booked_date_time": result.booked_date_time,
            "number_of_tickets": result.number_of_tickets,
            "toatal_time": result.toatal_time,
            "type_user":"Customer"
        } for result in list_result])


@app.route('/admin_feedback')
def admin_feedback():
    if not current_user.is_authenticated:
        return redirect(url_for('root'))
    feedback = db.session.query(ud.Feedback).all()
    return render_template("feedback.html", name=current_user.name, feedback=[
        {
            "name": ud.User.query.filter_by(id=f.user_id).first().name,
            "feedback": f.feedback_data,
            "id": f.id
        } for f in feedback])


@app.route('/feedback/delete/<feedback_id>', methods=["DELETE"])
def delete_feedback(feedback_id: str):
    admin_c: ud.Feedback = ud.Feedback.query.filter_by(id=feedback_id).first()
    db.session.delete(admin_c)
    db.session.commit()
    return {
        "message": "deleted"
    }


def get_ticket(bus_details: str):
    result: btd.Ticket = btd.Ticket.query.filter_by(id=bus_details).first()
    bus_no = result.bus_no
    if not str(result.bus_no).isspace() and len(result.bus_no) == 32:
        tem: brd.BusRoute = brd.BusRoute.query.filter_by(id=bus_no).first()
        bus_no = tem.bus_no
    starting_bus_stop = result.starting_bus_stop
    if not str(result.starting_bus_stop).isspace() and len(result.starting_bus_stop) == 32:
        tem: bsd.BusStops = bsd.BusStops.query.filter_by(id=starting_bus_stop).first()
        starting_bus_stop = tem.bus_stop
    end_bus_stop = result.end_bus_stop
    if not str(result.end_bus_stop).isspace() and len(result.end_bus_stop) == 32:
        tem: bsd.BusStops = bsd.BusStops.query.filter_by(id=end_bus_stop).first()
        end_bus_stop = tem.bus_stop
    return {
        "bus_no": bus_no,
        "starting_bus_stop": starting_bus_stop,
        "end_bus_stop": end_bus_stop,
        "timings_and_no_of_stop": result.timings_and_no_of_stop,
    }
