from app import app, login_manager
from database import admin_database as ad
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


from website import admin
