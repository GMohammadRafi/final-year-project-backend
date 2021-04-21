from app import app, db, user_database as ud, generate_ids as gids

from flask import request


@app.route('/user/feedback', methods=["POST"])
def feedback():
    user_id = request.form.get('user_id')
    user_feedback = request.form.get('feedback')
    uid = gids.generate_id(ud.Feedback)
    user_data = ud.Feedback(id=uid,
                            user_id=user_id,
                            feedback_data=user_feedback
                            )
    db.session.add(user_data)
    db.session.commit()
    return {
        "id": uid,
    }
