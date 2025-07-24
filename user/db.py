# db.py (inside user/)
import sqlite3

def init_db():
    conn = sqlite3.connect("penny.db")  # central DB
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            is_verified INTEGER NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("penny.db")
