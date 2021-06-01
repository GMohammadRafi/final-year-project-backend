# app.py
from flask import Flask, render_template, request, redirect, flash, jsonify, json
from flask_sqlalchemy import request, SQLAlchemy  # pip install flask-mysqldb https://github.com/alexferl/flask-mysqldb

app = Flask('__name__')
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mybmtc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mysql = SQLAlchemy(app)


@app.route('/')
def main():
    cursor = mysql.session.cursor()
    cur = mysql.session.cursor(MySQLdb.cursors.DictCursor)
    result = cur.execute("SELECT * FROM tbl_employee ORDER BY id")
    employee = cur.fetchall()
    return render_template('index.html', employee=employee)


@app.route('/insert', methods=['GET', 'POST'])
def insert():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        gender = request.form['gender']
        designation = request.form['designation']
        age = request.form['age']
        cur.execute("INSERT INTO tbl_employee (name, address, gender, designation, age) VALUES (%s, %s, %s, %s, %s)",
                    [name, address, gender, designation, age])
        mysql.connection.commit()
        cur.close()
    return jsonify('success')


@app.route('/select', methods=['GET', 'POST'])
def select():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        print(employee_id)
        result = cur.execute("SELECT * FROM tbl_employee WHERE id = %s", [employee_id])
        rsemployee = cur.fetchall()
        employeearray = []
        for rs in rsemployee:
            employee_dict = {
                'Id': rs['id'],
                'emp_name': rs['name'],
                'address': rs['address'],
                'gender': rs['gender'],
                'designation': rs['designation'],
                'age': rs['age']}
            employeearray.append(employee_dict)
        return json.dumps(employeearray)


if __name__ == '__main__':
    app.run(debug=True)
