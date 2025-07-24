# repositories/sqlite_user_repository.py
# uses sqlite3 to implement a user repository that interacts with a SQLite database.
# It provides methods to add a user and retrieve a user by email.
# repositories/sqlite_user_repository.py
import sqlite3
from ..Penny_user import User
from ..interfaces.userRepoInterface import IUserRepository

class SQLiteUserRepository(IUserRepository):

    def __init__(self, db_path="penny.db"):
        self.db_path = db_path
        # Ensure the connection and table exist when repository is created
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Ensure the users table exists when repository is initialized"""
        conn = sqlite3.connect(self.db_path)
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

    def add_user(self, user: User):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password, role, is_verified)
                VALUES (?, ?, ?, ?, ?)
            """, (user.username, user.email, user.password, user.role, int(user.is_verified)))
            conn.commit()
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> User:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
        finally:
            conn.close()