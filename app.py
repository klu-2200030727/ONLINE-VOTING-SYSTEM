import os
import random
import string
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import mysql.connector
from mysql.connector import Error
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Load environment variables from .env file securely
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# Configure Flask-Mail using env variables
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)
bcrypt = Bcrypt(app)

# MySQL Database configuration from environment
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', ''),
    'database': os.getenv('DB_NAME', 'online_voting')
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def generate_verification_code(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Decorators for user and admin login protection
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login required!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Admin login required.", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for('signup'))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('signup'))

        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "danger")
            return redirect(url_for('signup'))
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (email, username))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("User with this email or username already exists.", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for('signup'))

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        verification_code = generate_verification_code()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, is_verified, verification_code, blocked) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, email, password_hash, False, verification_code, False)
        )
        conn.commit()

        # Send verification email
        verification_link = url_for('verify_email', code=verification_code, _external=True)
        html_body = render_template('email_verification.html', verification_link=verification_link, username=username)
        msg = Message(subject="Verify your Online Voting System account",
                      recipients=[email],
                      html=html_body)
        try:
            mail.send(msg)
            flash("Verification email sent. Please check your inbox.", "success")
        except Exception as e:
            print(f"Error sending email: {e}")
            flash("Failed to send verification email. Contact admin.", "danger")

        cursor.close()
        conn.close()

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/verify_email/<code>')
def verify_email(code):
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return redirect(url_for('login'))
    cursor = conn.cursor()
    cursor.execute("SELECT id, is_verified FROM users WHERE verification_code=%s", (code,))
    user = cursor.fetchone()
    if user:
        user_id, is_verified = user
        if not is_verified:
            cursor.execute("UPDATE users SET is_verified=TRUE, verification_code=NULL WHERE id=%s", (user_id,))
            conn.commit()
            flash("Email verified successfully! You can now login.", "success")
        else:
            flash("Email already verified. Please login.", "info")
    else:
        flash("Invalid or expired verification link.", "danger")
    cursor.close()
    conn.close()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for('login'))

        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "danger")
            return redirect(url_for('login'))
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('login'))
        if user['blocked']:
            flash("Your account is blocked. Contact admin.", "danger")
            return redirect(url_for('login'))
        if not user['is_verified']:
            flash("Email not verified. Please check your inbox.", "warning")
            return redirect(url_for('login'))
        if not bcrypt.check_password_hash(user['password_hash'], password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for('login'))

        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for('contestants'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/contestants')
@login_required
def contestants():
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return redirect(url_for('home'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contestants")
    contestants_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('contestants.html', contestants=contestants_list)

@app.route('/about/<int:c_id>')
@login_required
def about_contestant(c_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return redirect(url_for('contestants'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contestants WHERE id=%s", (c_id,))
    contestant = cursor.fetchone()
    cursor.close()
    conn.close()
    if not contestant:
        flash("Contestant not found.", "danger")
        return redirect(url_for('contestants'))
    return render_template('about.html', contestant=contestant)

@app.route('/vote/<int:c_id>')
@login_required
def vote(c_id):
    user_id = session.get('user_id')
    conn = get_db_connection()
    if not conn:
        flash("Database connection error.", "danger")
        return redirect(url_for('contestants'))
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT has_voted FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        flash("User not found. Please login again.", "danger")
        return redirect(url_for('login'))
    if user['has_voted']:
        cursor.close()
        conn.close()
        return redirect(url_for('vote_fail'))
    cursor.execute("SELECT votes FROM contestants WHERE id=%s", (c_id,))
    contestant = cursor.fetchone()
    if not contestant:
        cursor.close()
        conn.close()
        flash("Contestant not found.", "danger")
        return redirect(url_for('contestants'))
    new_votes = contestant['votes'] + 1
    cursor.execute("UPDATE contestants SET votes=%s WHERE id=%s", (new_votes, c_id))
    cursor.execute("UPDATE users SET has_voted=TRUE WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('vote_success'))

@app.route('/vote_success')
@login_required
def vote_success():
    return render_template('vote_success.html')

@app.route('/vote_fail')
@login_required
def vote_fail():
    return render_template('vote_fail.html')

# Admin login checks fixed username/password 'admin'/'admin'
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash("Admin logged in successfully.", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin credentials.", "danger")
    return render_template('admin_login.html')

@app.route('/admin/logout')
@admin_login_required
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash("Admin logged out.", "info")
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, username, email, blocked FROM users ORDER BY id DESC")
    users = cursor.fetchall()

    cursor.execute("SELECT id, name, votes FROM contestants ORDER BY id DESC")
    contestants = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', users=users, contestants=contestants)

@app.route('/admin/add_contestant', methods=['GET', 'POST'])
@admin_login_required
def admin_add_contestant():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash("Contestant name is required.", "danger")
            return redirect(url_for('admin_add_contestant'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contestants (name, description) VALUES (%s, %s)", (name, description))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Contestant '{name}' added successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_add_contestant.html')

@app.route('/admin/delete_contestant/<int:c_id>', methods=['POST'])
@admin_login_required
def admin_delete_contestant(c_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contestants WHERE id=%s", (c_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Contestant deleted successfully.", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_user_block/<int:user_id>', methods=['POST'])
@admin_login_required
def admin_toggle_user_block(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT blocked FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        flash("User not found.", "danger")
        return redirect(url_for('admin_dashboard'))

    new_status = not user['blocked']
    cursor.execute("UPDATE users SET blocked=%s WHERE id=%s", (new_status, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    msg = "User blocked successfully." if new_status else "User unblocked successfully."
    flash(msg, "success")
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
