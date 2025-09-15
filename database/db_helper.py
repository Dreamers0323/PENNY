import sqlite3
import os
from . import db  # Import your existing db module

def get_user_by_username(username):
    """Get user by username from the database"""
    conn = db.get_db_connection()  # Use your existing connection method
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'SELECT id, username, password_hash, full_name, email FROM users WHERE username = ?', 
            (username,)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def create_user(username, password_hash, full_name, email):
    """Create a new user in the database"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash, full_name, email) VALUES (?, ?, ?, ?)',
            (username, password_hash, full_name, email)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # User already exists
        return None
    finally:
        conn.close()

def user_exists(username, email):
    """Check if a user with the given username or email already exists"""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()