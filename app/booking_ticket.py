from app import app, generate_ids as gids, user_database as ud, db
from flask import request
from os import path, mkdir
from werkzeug.utils import secure_filename

APP_ROOT = path.dirname(path.abspath(__file__))
IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG"]


@app.route('/book-ticket/face-id', methods=["POST"])
def upload_image():
    url = []
    if request.files:
        target = path.join(APP_ROOT, 'images/')
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
def register():
    user_data = ud.BookTicket(
        id=gids.generate_id(ud.User),
        booked_user_id=request.form.get('booked_user_id'),
        bus_no=request.form.get('bus_no'),
        starting_bus_stop=request.form.get('starting_bus_stop'),
        end_bus_stop=request.form.get('end_bus_stop'),
        starting_bus_timing=request.form.get('starting_bus_timing'),
        timings_and_no_of_stop=request.form.get('timings_and_no_of_stop'),
        face_id=request.form.get('face_id'),
        payment_states=bool(request.form.get('payment_states'))
    )
    db.session.add(user_data)
    db.session.commit()
    return {
        "message": "Booked Ticket"}


def allowed_image(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in IMAGE_EXTENSIONS:
        return True
    else:
        return False
