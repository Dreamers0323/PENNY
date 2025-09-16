# database/db_helper.py
# This module provides helper functions for database operations using SQLite.
import sqlite3
import os
from . import db  # Import your existing db module
from threading import local

# Thread-local storage for database connections
thread_local = local()

def get_db_connection():
    """Get a database connection for the current thread"""
    if not hasattr(thread_local, 'db_connection'):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'penny.db')
        thread_local.db_connection = sqlite3.connect(db_path)
        thread_local.db_connection.row_factory = sqlite3.Row
    return thread_local.db_connection

def close_db_connection(e=None):
    """Close the database connection for the current thread"""
    if hasattr(thread_local, 'db_connection'):
        thread_local.db_connection.close()
        del thread_local.db_connection

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