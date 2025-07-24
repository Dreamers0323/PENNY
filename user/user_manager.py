# user/user_manager.py
# this code defines functions to manage user registration and login.
# It uses a SQLite database to store user information.

from database.db import get_connection

def register_user(name, email, password, user_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password, user_type)
        VALUES (?, ?, ?, ?)
    """, (name, email, password, user_type))
    conn.commit()
    conn.close()

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE email = ? AND password = ?
    """, (email, password))
    user = cursor.fetchone()
    conn.close()
    return user
