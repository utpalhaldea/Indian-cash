import os
import re
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "users.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-a-long-random-secret")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # Enable only when deployed behind HTTPS:
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL UNIQUE,
                email TEXT,
                password_hash TEXT NOT NULL,
                referral_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip() or None
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        referral_code = request.form.get("referral_code", "").strip() or None

        if len(full_name) < 2:
            flash("Please enter your full name.", "error")
        elif not re.fullmatch(r"[0-9]{10}", phone):
            flash("Enter a valid 10-digit Indian mobile number.", "error")
        elif email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        else:
            try:
                with get_db() as conn:
                    conn.execute(
                        """INSERT INTO users
                           (full_name, phone, email, password_hash, referral_code)
                           VALUES (?, ?, ?, ?, ?)""",
                        (full_name, phone, email, generate_password_hash(password), referral_code)
                    )
                flash("Account created. You can now log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("An account with this phone number already exists.", "error")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            return redirect(url_for("dashboard"))
        flash("Incorrect phone number or password.", "error")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", full_name=session.get("full_name", "User"))

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    # Safe starter placeholder: real password reset needs verified email/SMS,
    # expiring one-time tokens, rate limiting, and delivery integration.
    if request.method == "POST":
        flash("Password reset is not configured yet. Contact the site administrator.", "error")
    return render_template("forgot_password.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
