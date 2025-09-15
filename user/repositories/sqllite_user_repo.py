# repositories/sqlite_user_repository.py
# uses sqlite3 to implement a user repository that interacts with a SQLite database.
# It provides methods to add a user and retrieve a user by email.
# repositories/sqlite_user_repository.py
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
        except sqlite3.IntegrityError as e:
            # This will catch duplicate email/username errors
            raise ValueError(f"User with this email or username already exists: {str(e)}")
        except sqlite3.Error as e:
            raise Exception(f"Database error during user creation: {str(e)}")
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

    def find_by_username(self, username: str):
        """Find a user by their username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
    
        try:
            # Fixed: Use 'password' instead of 'password_hash' to match your table schema
            cursor.execute(
                'SELECT id, username, email, password, role, is_verified FROM users WHERE username = ?',
                (username,)
            )
            row = cursor.fetchone()
        
            if row:
                # Create User object with the correct parameters (matches your table columns)
                return User(
                    user_id=row[0],
                    username=row[1], 
                    email=row[2],
                    password=row[3],
                    role=row[4],
                    is_verified=bool(row[5])
                )
            return None
        
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")
        finally:
            conn.close()

    # Add this method to check if username exists
    def username_exists(self, username: str) -> bool:
        """Check if a username already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    # Add this method to check if email exists  
    def email_exists(self, email: str) -> bool:
        """Check if an email already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            return cursor.fetchone() is not None
        finally:
            conn.close()