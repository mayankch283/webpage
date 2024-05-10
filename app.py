from flask import Flask, jsonify, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('restaurant.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=? AND user_type=?", (username, password, user_type))
        user = c.fetchone()
        if user:
            session['user_id'] = user[0]
            session['user_type'] = user_type
            if user_type == 'user':
                redirect_url = url_for('user_dashboard')
            else:
                redirect_url = url_for('manager_dashboard')
            return jsonify({'status': 'success', 'redirect_url': redirect_url})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'})
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        db = get_db()
        c = db.cursor()
        try:
            c.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", (username, password, user_type))
            db.commit()
            return jsonify({'status': 'success', 'message': 'Registration successful'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    return render_template('register.html')

@app.route('/user_dashboard', methods=['GET'])
def user_dashboard():
    if 'user_id' in session and session['user_type'] == 'user':
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM restaurants")
        restaurants = c.fetchall()
        c.execute("SELECT id, username FROM users WHERE user_type = 'manager'")
        managers = c.fetchall()
        return render_template('user_dashboard.html', restaurants=restaurants, managers=managers)
    else:
        return 'Unauthorized access'

@app.route('/manager_dashboard', methods=['GET'])
def manager_dashboard():
    if 'user_id' in session and session['user_type'] == 'manager':
        db = get_db()
        c = db.cursor()
        c.execute("""
            SELECT o.id, o.user_id, o.restaurant_id, o.items, o.status
            FROM orders o
            WHERE o.restaurant_id = (SELECT id FROM users WHERE id = ? AND user_type = 'manager')
        """, (session['user_id'],))
        orders = c.fetchall()
        return render_template('manager_dashboard.html', orders=orders)
    else:
        return 'Unauthorized access'

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' in session and session['user_type'] == 'user':
        restaurant_id = request.form['restaurant_id']
        items = request.form['items']
        db = get_db()
        c = db.cursor()
        try:
            manager_id = c.execute("SELECT id FROM users WHERE id = ? AND user_type = 'manager'", (restaurant_id,)).fetchone()[0]
            if manager_id:
                c.execute("INSERT INTO orders (user_id, restaurant_id, items, status) VALUES (?, ?, ?, ?)", (session['user_id'], manager_id, items, 'Pending'))
                db.commit()
                return 'Order placed successfully'
            else:
                return 'Invalid restaurant ID'
        except Exception as e:
            db.rollback()
            return str(e)
    else:
        return 'Unauthorized access'

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    if 'user_id' in session and session['user_type'] == 'manager':
        order_id = request.form['order_id']
        status = request.form['status']
        db = get_db()
        c = db.cursor()
        c.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        db.commit()
        return 'Order status updated'
    else:
        return 'Unauthorized access'

if __name__ == '__main__':
    app.run(debug=True)