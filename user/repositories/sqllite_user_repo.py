# repositories/sqlite_user_repository.py
# uses sqlite3 to implement a user repository that interacts with a SQLite database.
# It provides methods to add a user and retrieve a user by email.
import sqlite3
from Penny_user import User
from interfaces.userRepoInterface import IUserRepository

class SQLiteUserRepository(IUserRepository):

    def __init__(self, db_path="users.db"):
        self.db_path = db_path

    def add_user(self, user: User):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password, role, is_verified)
            VALUES (?, ?, ?, ?, ?)
        """, (user.username, user.email, user.password, user.role, int(user.is_verified)))
        conn.commit()
        conn.close()

    def get_user_by_email(self, email: str) -> User:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(*row)
        return None
