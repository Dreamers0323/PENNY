# init_db.py

import sqlite3

def init_database(db_path="penny.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        is_verified INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized and 'users' table created.")

if __name__ == "__main__":
    init_database()
