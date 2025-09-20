# purchases/savings.py
import sqlite3
from database.db import get_connection
from database.db_helper import get_db_connection

class SavingsGoals:
    def __init__(self, user_id):
        self.user_id = user_id
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
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
        self.conn.commit()

    def add_goal(self, goal_name, target_amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO savings_goals (user_id, goal_name, target_amount, saved_amount)
            VALUES (?, ?, ?, 0)
        """, (self.user_id, goal_name, target_amount))
        conn.commit()

    def update_saved_amount(self, goal_name, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE savings_goals
            SET saved_amount = saved_amount + ?
            WHERE user_id = ? AND goal_name = ?
        """, (amount, self.user_id, goal_name))
        conn.commit()

    def get_goals(self):
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
                'goal_name': row['goal_name'],
                'target_amount': row['target_amount'],
                'saved_amount': row['saved_amount']
            })
        return result

    def delete_goal(self, goal_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM savings_goals
            WHERE user_id = ? AND goal_name = ?
        """, (self.user_id, goal_name))
        conn.commit()