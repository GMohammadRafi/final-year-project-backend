import cv2
from PIL import Image
from numpy import asarray
from keras_vggface.utils import preprocess_input
from os import path
from matplotlib import pyplot
from app import app, all_images_encoding, ml_methods as mlm, all_images, constants as c
from database import book_ticket_database as btd, conductor_database as cd, user_database as ud, \
    bus_route_database as brd, bus_stops_database as bsd, db
from flask import Response, request
from datetime import datetime
from pytz import timezone
from sqlalchemy import or_

time_zone = timezone('Asia/Kolkata')
camera = cv2.VideoCapture(0)
booked_user_encoding = []
booked_user_files = []
unbooked_user_encoding = []
unbooked_user_files = []


def gen_frames(conductor_id):
    while True:
        setting_booked_face_id(conductor_id)
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            faces = mlm.detector.detect_faces(frame)
            if len(faces) != 0:
                for face in faces:
                    x, y, width, height = face['box']
                    x2, y2 = x + width, y + height
                    try:
                        image = Image.fromarray(frame[y:y2, x:x2]).resize((224, 224))
                        array_image = []
                        array_image.append(asarray(image))
                        samples = asarray(array_image, 'float32')
                        samples = preprocess_input(samples, version=1)
                        unpre = mlm.model.predict(samples)
                        machFound = False
                        for data in booked_user_encoding:
                            if mlm.is_match(data, unpre):
                                machFound = True
                                break
                        if machFound:
                            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)
                            setting_ticket_to_using(conductor_id)
                        else:
                            machFound = False
                            for data in unbooked_user_encoding:
                                if mlm.is_match(data, unpre):
                                    machFound = True
                                    break
                            if machFound:
                                cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 255), 2)
                            else:
                                cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 255), 2)
                                image_name = f"{conductor_id}{str(datetime.now(time_zone)).replace(':', '').replace(' ', '')}.jpg"
                                all_images_encoding.append(unpre)
                                unbooked_user_encoding.append(unpre)
                                unbooked_user_files.append(image_name)
                                all_images.append(image_name)
                                cv2.imwrite(path.join(mlm.images_folder,
                                                      image_name),
                                            frame)
                    except:
                        print("Out Of Box")
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed/<conductor_id>')
def video_feed(conductor_id):
    return Response(gen_frames(conductor_id), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/scan/face-id/<conductor_id>', methods=["POST"])
def scan_face_id(conductor_id):
    target = path.join(c.APP_ROOT, 'images')
    setting_booked_face_id(conductor_id)
    if request.files:
        file = request.files.get("images")
        file.save(path.join(target, "scan.jpg"))
        frame = pyplot.imread(path.join(target, "scan.jpg"))
        faces = mlm.detector.detect_faces(frame)
        if len(faces) != 0:
            for face in faces:
                x, y, width, height = face['box']
                x2, y2 = x + width, y + height
                try:
                    image = Image.fromarray(frame[y:y2, x:x2]).resize((224, 224))
                    array_image = []
                    array_image.append(asarray(image))
                    samples = asarray(array_image, 'float32')
                    samples = preprocess_input(samples, version=1)
                    unpre = mlm.model.predict(samples)
                    machFound = False
                    for data in booked_user_encoding:
                        if mlm.is_match(data, unpre):
                            machFound = True
                            break
                    if machFound:
                        setting_ticket_to_using(conductor_id)
                        return {
                                   "result": "User booked ticket"
                               }, 200
                    else:
                        machFound = False
                        for data in unbooked_user_encoding:
                            if mlm.is_match(data, unpre):
                                machFound = True
                                break
                        if machFound:
                            return {
                                       "result": "User did not book a ticket"
                                   }, 300
                        else:
                            image_name = f"{conductor_id}{str(datetime.now(time_zone)).replace(':', '').replace(' ', '')}.jpg"
                            all_images_encoding.append(unpre)
                            unbooked_user_encoding.append(unpre)
                            unbooked_user_files.append(image_name)
                            all_images.append(image_name)
                            cv2.imwrite(path.join(mlm.images_folder,
                                                  image_name),
                                        frame)
                            return {
                                       "result": "User did not book a ticket"
                                   }, 300
                except:
                    return {
                               "result": "No Face Found"
                           }, 300


@app.route('/conductor/all/booked-tickets/<conductor_id>', methods=["POST"])
def all_tickets_of_route(conductor_id):
    current_position: cd.CurrentPosition = cd.CurrentPosition.filter_by(conductor_id=conductor_id).first()
    current_bus_running: cd.RunningBuses = cd.RunningBuses.filter_by(conductor_id=conductor_id, status=True).first()
    tickets_booked_by_conductor = btd.TicketsBookedByConductor.filter_by(conductor_id=conductor_id, status=4).all()
    booked_tickets = db.session.query(btd.BookedTickets).all()
    tickets_booked_by_users = btd.Ticket.filter(btd.Ticket.bus_no == current_bus_running.bus_route_id,
                                                or_(btd.Ticket.status == 4, btd.Ticket.status == 0)).all()
    ticket_details = []
    tdc: btd.TicketsBookedByConductor
    for tdc in tickets_booked_by_conductor:
        ticket_details.append({
            "status": tdc.status,
            "face_id": tdc.face_id,
            "end_bus_id": tdc.end_bus_id,
            "starting_bus_id": tdc.starting_bus_id,
            "amount_payed": tdc.amount_payed,
            "number_of_tickets": tdc.number_of_tickets,
        })
    tdu: btd.Ticket
    for tdu in tickets_booked_by_users:
        b: btd.BookedTickets
        for b in booked_tickets:
            if tdu.id in b.tickets:
                ticket_details.append(
                    {
                        "status": tdu.status,
                        "face_id": b.face_id,
                        "end_bus_id": tdu.end_bus_stop,
                        "starting_bus_id": tdu.starting_bus_stop,
                        "amount_payed": b.amount_payed,
                        "number_of_tickets": b.number_of_tickets,
                    }
                )
                break
    return {
        "tickets": ticket_details
    }


def setting_booked_face_id(conductor_id):
    booked_user_encoding.clear()
    booked_user_files.clear()
    unbooked_user_encoding.clear()
    unbooked_user_files.clear()
    list_stop_id = []
    face_ids = []
    try:
        current_position: cd.CurrentPosition = cd.CurrentPosition.query.filter_by(conductor_id=conductor_id).first()

        current_bus_running: cd.RunningBuses = cd.RunningBuses.query.filter_by(conductor_id=conductor_id,
                                                                               status=True).first()
        tickets_booked_by_conductor = btd.TicketsBookedByConductor.query.filter_by(conductor_id=conductor_id,
                                                                                   status=4).all()
        booked_tickets = db.session.query(btd.BookedTickets).all()
        tickets_booked_by_users = btd.Ticket.query.filter(btd.Ticket.bus_no == current_bus_running.bus_route_id,
                                                          or_(btd.Ticket.status == 4, btd.Ticket.status == 0)).all()
        bus_stops: brd.BusRoute = brd.BusRoute.query.filter_by(id=current_position.bus_route_id).first()

        for stop in bus_stops.list_of_bus_stops:
            list_stop_id.append(stop["id"])


        tdc: btd.TicketsBookedByConductor
        for tdc in tickets_booked_by_conductor:
            face_ids.extend(tdc.face_id)

        tdu: btd.Ticket
        for tdu in tickets_booked_by_users:
            pending_stops_ids = list_stop_id[list_stop_id.index(tdu.starting_bus_stop):list_stop_id.index(tdu.end_bus_stop):-1] if current_bus_running.through_loc else list_stop_id[
                                                                                                 list_stop_id.index(tdu.starting_bus_stop):list_stop_id.index(tdu.end_bus_stop)+1]
            print(pending_stops_ids)
            print(current_position.passed_bus_stop_id)
            print(current_position.passed_bus_stop_id in pending_stops_ids)
            # TODO::
            b: btd.BookedTickets
            for b in booked_tickets:
                if tdu.id in b.tickets and current_position.passed_bus_stop_id in pending_stops_ids:
                    face_ids.extend(b.face_id)
                    break
    except:
        pass
    for d in face_ids:
        if d in all_images:
            index = all_images.index(d)
            booked_user_files.append(all_images[index])
            booked_user_encoding.append(all_images_encoding[index])
    for a in all_images:
        if a is not booked_user_files:
            index = all_images.index(a)
            unbooked_user_files.append(all_images[index])
            unbooked_user_encoding.append(all_images_encoding[index])


def setting_ticket_to_using(conductor_id):
    current_bus_running: cd.RunningBuses = cd.RunningBuses.query.filter_by(conductor_id=conductor_id,
                                                                           status=True).first()
    tickets_booked_by_conductor = btd.TicketsBookedByConductor.query.filter_by(conductor_id=conductor_id,
                                                                               status=4).all()
    booked_tickets = db.session.query(btd.BookedTickets).all()
    tickets_booked_by_users = btd.Ticket.query.filter_by(bus_no=current_bus_running.bus_route_id, status=0).all()
    tbu: btd.Ticket
    for tbu in tickets_booked_by_users:
        tbu.status = 4
    db.session.commit()
