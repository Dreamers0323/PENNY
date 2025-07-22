# user/user_manager.py

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
