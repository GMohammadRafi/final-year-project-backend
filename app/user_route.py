from app import app, generate_ids as gids
from database import user_database as ud, db

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


@app.route('/user/wallet-amount', methods=["GET"])
def wallet_amount():
    user_id = request.form.get('user_id')
    user_data: ud.User = ud.User.query.filter_by(id=user_id).first()
    if not user_data:
        return {
                   "message": "User Do Not Exist"
               }, 404
    return {
        "amount": user_data.amount,
    }


@app.route('/user/add/wallet-amount', methods=["GET"])
def add_wallet_amount():
    user_id = request.form.get('user_id')
    amount = request.form.get('amount')
    user_data: ud.User = ud.User.query.filter_by(id=user_id).first()
    if not user_data:
        return {
                   "message": "User Do Not Exist"
               }, 404
    user_data.amount = amount
    db.session.commit()
    return {
        "message": "Updated",
    }
