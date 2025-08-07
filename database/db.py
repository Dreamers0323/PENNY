# database/db.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'penny.db')

def get_connection(db_path=None):
    """Get a connection to the database. Optionally specify a path."""
    if db_path is None:
        db_path = DB_PATH
    return sqlite3.connect(db_path)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_type TEXT CHECK(user_type IN ('customer', 'employee')) NOT NULL
        )
    """)

    # Accounts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            account_type TEXT,
            balance REAL DEFAULT 0.0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Loans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            principal REAL,
            interest_rate REAL,
            term_months INTEGER,
            loan_type TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Purchases Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item TEXT,
            amount REAL,
            date TEXT,
            category TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
