from flask import Flask, render_template, redirect, url_for, request
import db

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form['username']
    password = request.form['password']
    category = request.form['category']

    # Here you should add your authentication logic
    # For example, you can check if the username and password are valid
    # and if the user belongs to the selected category

    if category == 'user':
        return redirect(url_for('endpoint1'))
    elif category == 'hotel_manager':
        return redirect(url_for('endpoint2'))
    else:
        return "Invalid category"

@app.route('/endpoint1')
def endpoint1():
    hotels = db.load_hotels('hotels.json')
    return render_template('endpoint1.html', hotels=hotels)

@app.route('/endpoint2')
def endpoint2():
    orders = db.load_orders('orders.json')
    return render_template('endpoint2.html', orders=orders)
if __name__ == '__main__':
    app.run(debug=True)