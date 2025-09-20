# purchases/savings.py
from database.db_helper import get_db_connection

class SavingsGoals:
    def __init__(self, user_id):
        self.user_id = user_id
        self.create_table()

    def create_table(self):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS savings_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    goal_name TEXT,
                    target_amount REAL,
                    saved_amount REAL
                )
            """)
            conn.commit()
        finally:
            if conn:
                conn.close()

    def add_goal(self, goal_name, target_amount):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO savings_goals (user_id, goal_name, target_amount, saved_amount)
                VALUES (?, ?, ?, 0)
            """, (self.user_id, goal_name, target_amount))
            conn.commit()
        finally:
            if conn:
                conn.close()

    def update_saved_amount(self, goal_name, amount):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE savings_goals
                SET saved_amount = saved_amount + ?
                WHERE user_id = ? AND goal_name = ?
            """, (amount, self.user_id, goal_name))
            conn.commit()
        finally:
            if conn:
                conn.close()

    def get_goals(self):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT goal_name, target_amount, saved_amount
                FROM savings_goals
                WHERE user_id = ?
            """, (self.user_id,))
            
            goals = cursor.fetchall()
            result = []
            for row in goals:
                result.append({
                    'goal_name': row[0],  # Use index instead of column name
                    'target_amount': row[1],
                    'saved_amount': row[2]
                })
            return result
        finally:
            if conn:
                conn.close()

    def delete_goal(self, goal_name):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM savings_goals
                WHERE user_id = ? AND goal_name = ?
            """, (self.user_id, goal_name))
            conn.commit()
        finally:
            if conn:
                conn.close()