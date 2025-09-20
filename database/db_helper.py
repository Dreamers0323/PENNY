# database/db_helper.py
# This module provides helper functions for database operations using SQLite.
# Updated database/db_helper.py with better connection handling

import sqlite3
import os
import threading
import time

# Add connection timeout and better error handling
def get_db_connection():
    """Get a fresh database connection with timeout"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'penny.db')
    
    # Try multiple times with increasing timeout
    for attempt in range(3):
        try:
            conn = sqlite3.connect(db_path, timeout=20.0)  # 20 second timeout
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency (optional)
            conn.execute('PRAGMA journal_mode=WAL')
            return conn
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < 2:
                print(f"Database locked, retrying... (attempt {attempt + 1})")
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                continue
            else:
                raise

def close_db_connection(conn=None):
    """Close the provided database connection safely"""
    if conn:
        try:
            conn.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

def execute_with_retry(query, params=None, fetch=False):
    """Execute a query with automatic retry on database lock"""
    for attempt in range(3):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall() if fetch == 'all' else cursor.fetchone()
            else:
                result = cursor.lastrowid
                
            conn.commit()
            return result
            
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < 2:
                print(f"Database locked during query, retrying... (attempt {attempt + 1})")
                time.sleep(0.5 * (attempt + 1))
                continue
            else:
                raise
        finally:
            if conn:
                conn.close()

def get_user_by_username(username):
    """Get user by username from the database"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, password_hash, full_name, email FROM users WHERE username = ?', 
            (username,)
        )
        return cursor.fetchone()
    finally:
        if conn:
            conn.close()

def create_user(username, password_hash, full_name, email):
    """Create a new user in the database with retry logic"""
    for attempt in range(3):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, password_hash, full_name, email) VALUES (?, ?, ?, ?)',
                (username, password_hash, full_name, email)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # User already exists
            return None
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < 2:
                print(f"Database locked during user creation, retrying... (attempt {attempt + 1})")
                time.sleep(0.5 * (attempt + 1))
                continue
            else:
                raise
        finally:
            if conn:
                conn.close()

def user_exists(username, email):
    """Check if a user with the given username or email already exists"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        )
        return cursor.fetchone() is not None
    finally:
        if conn:
            conn.close()