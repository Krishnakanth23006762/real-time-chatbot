import sqlite3
import hashlib
import os
import secrets
from datetime import datetime, timedelta

DB_FILE = "user_database.db"

def hash_password(password):
    """Hashes the password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def db_connect():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def setup_database():
    """Creates the users table if it doesn't already exist."""
    if not os.path.exists(DB_FILE):
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                reset_token TEXT,
                token_expiry DATETIME
            )
        ''')
        conn.commit()
        conn.close()
        print("Database and users table created.")

def add_user(email, password):
    """Adds a new user to the database."""
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # This error occurs if the email is already in use
        return False
    finally:
        conn.close()

def verify_user(email, password):
    """Verifies a user's email and password."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

def set_reset_token(email):
    """Generates and stores a password reset token for a user."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if user:
        token = secrets.token_urlsafe(20)
        expiry = datetime.now() + timedelta(hours=1) # Token is valid for 1 hour
        cursor.execute("UPDATE users SET reset_token = ?, token_expiry = ? WHERE email = ?", (token, expiry, email))
        conn.commit()
        conn.close()
        return token
    conn.close()
    return None

def reset_password(token, new_password):
    """Resets a user's password using a valid token."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT email, token_expiry FROM users WHERE reset_token = ?", (token,))
    result = cursor.fetchone()
    if result:
        email, token_expiry_str = result
        token_expiry = datetime.strptime(token_expiry_str, '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() < token_expiry:
            # Token is valid, update password and clear token
            cursor.execute("UPDATE users SET password_hash = ?, reset_token = NULL, token_expiry = NULL WHERE email = ?", (hash_password(new_password), email))
            conn.commit()
            conn.close()
            return True
    conn.close()
    return False
