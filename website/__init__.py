from app import app
from flask import render_template


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/admin-login')
def admin_login():
    return render_template('admin_login.html')


@app.route('/customer-login')
def customer_login():
    return render_template('customer_login.html')
