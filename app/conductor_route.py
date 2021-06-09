from app import app, generate_ids as gids
from flask import request
from database import db, conductor_database as cd


@app.route('/conductor/current-running-bus', methods=["POST"])
def current_running_bus():
    conductor_id = request.form.get('conductor_id')
    bus_route_id = request.form.get('bus_route_id')
    through_loc = request.form.get('through_loc')
    result: cd.RunningBuses = cd.RunningBuses.query.filter_by(conductor_id=conductor_id).first()
    if result:
        result.bus_route_id = bus_route_id
        result.through_loc = bool(int(through_loc))

    else:
        result = cd.RunningBuses(id=gids.generate_id(cd.RunningBuses), conductor_id=conductor_id,
                                                 bus_route_id=bus_route_id, through_loc=bool(int(through_loc)))
        db.session.add(result)
    db.session.commit()
    return {
        "id": result.id, "conductor_id": conductor_id, "bus_route_id": bus_route_id, "through_loc": through_loc
    }


# @app.route('/conductor/live-location', methods=["POST"])
# def current_running_bus():
#     conductor_id = request.form.get('id')
#     bus_route_id = request.form.get('bus_route_id')
#     through_loc = request.form.get('through_loc')
#     result: cd.RunningBuses = cd.RunningBuses.query.filter_by(conductor_id=conductor_id).first()
#     if result:
#         result.bus_route_id = bus_route_id
#         result.through_loc = through_loc
#     else:
#         result = cd.RunningBuses.query.filter_by(id=gids.generate_id(cd.RunningBuses), conductor_id=conductor_id,
#                                                  bus_route_id=bus_route_id, through_loc=through_loc)
#         db.session.add(result)
#     db.session.commit()
#     return {
#         "id": result.id, "conductor_id": conductor_id, "bus_route_id": bus_route_id, "through_loc": through_loc
#     }
