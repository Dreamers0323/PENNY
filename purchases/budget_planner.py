# budget_planner.py
# This module handles budget planning functionalities
# It allows users to set budgets, update them, and view summaries

from datetime import datetime
from database.db_helper import get_db_connection

class BudgetPlanner:
    def __init__(self):
        self._create_tables()

    def _create_tables(self):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budget (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    category TEXT,
                    amount REAL,
                    month TEXT,
                    year INTEGER,
                    created_at TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS overall_budget (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    total_amount REAL,
                    month TEXT,
                    year INTEGER,
                    created_at TEXT
                )
            """)
            conn.commit()
        finally:
            if conn:
                conn.close()

    def set_overall_budget(self, user_id, total_amount, month=None, year=None):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            month = month or datetime.now().strftime("%B")
            year = year or datetime.now().year
            created_at = datetime.now().isoformat()

            cursor.execute("""
                SELECT * FROM overall_budget WHERE user_id = ? AND month = ? AND year = ?
            """, (user_id, month, year))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE overall_budget SET total_amount = ?, created_at = ? 
                    WHERE user_id = ? AND month = ? AND year = ?
                """, (total_amount, created_at, user_id, month, year))
            else:
                cursor.execute("""
                    INSERT INTO overall_budget (user_id, total_amount, month, year, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, total_amount, month, year, created_at))
            
            conn.commit()
            print(f"Overall budget of ZMW {total_amount} set for {month}, {year}")
        finally:
            if conn:
                conn.close()

    def set_budget(self, user_id, category, amount, month=None, year=None):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            month = month or datetime.now().strftime("%B")
            year = year or datetime.now().year
            created_at = datetime.now().isoformat()

            cursor.execute("""
                SELECT * FROM budget WHERE user_id = ? AND category = ? AND month = ? AND year = ?
            """, (user_id, category, month, year))

            if cursor.fetchone():
                self.update_budget(user_id, category, amount, month, year)
                return

            cursor.execute("""
                INSERT INTO budget (user_id, category, amount, month, year, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, category, amount, month, year, created_at))
            conn.commit()

            print(f"Budget set: {category} - ZMW {amount} for {month}, {year}")
        finally:
            if conn:
                conn.close()

    def update_budget(self, user_id, category, new_amount, month=None, year=None):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            month = month or datetime.now().strftime("%B")
            year = year or datetime.now().year

            cursor.execute("""
                UPDATE budget
                SET amount = ?
                WHERE user_id = ? AND category = ? AND month = ? AND year = ?
            """, (new_amount, user_id, category, month, year))
            conn.commit()

            print(f"Updated {category} budget to ZMW {new_amount} for {month}, {year}")
        finally:
            if conn:
                conn.close()

    def get_budgets(self, user_id, month=None, year=None):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            month = month or datetime.now().strftime("%B")
            year = year or datetime.now().year

            cursor.execute("""
                SELECT category, amount, month, year FROM budget
                WHERE user_id = ? AND month = ? AND year = ?
            """, (user_id, month, year))

            budgets = cursor.fetchall()
            result = []
            for row in budgets:
                result.append({
                    'category': row[0],  # Use index instead of column name
                    'amount': row[1],
                    'month': row[2],
                    'year': row[3]
                })
            return result
        finally:
            if conn:
                conn.close()

    def get_budget_summary(self, user_id, month=None, year=None):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            month = month or datetime.now().strftime("%B")
            year = year or datetime.now().year

            cursor.execute("""
                SELECT total_amount FROM overall_budget
                WHERE user_id = ? AND month = ? AND year = ?
            """, (user_id, month, year))
            total_budget_row = cursor.fetchone()

            if not total_budget_row:
                return None

            total_budget = total_budget_row[0]  # Use index instead of column name

            cursor.execute("""
                SELECT SUM(amount) as total_spent FROM budget
                WHERE user_id = ? AND month = ? AND year = ?
            """, (user_id, month, year))

            total_spent_row = cursor.fetchone()
            total_spent = total_spent_row[0] or 0.0  # Use index instead of column name
            remaining = total_budget - total_spent

            return {
                'total_budget': total_budget,
                'total_spent': total_spent,
                'remaining': remaining
            }
        finally:
            if conn:
                conn.close()

    def delete_budget_category(self, user_id, category, month=None, year=None):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            month = month or datetime.now().strftime("%B")
            year = year or datetime.now().year

            cursor.execute("""
                DELETE FROM budget
                WHERE user_id = ? AND category = ? AND month = ? AND year = ?
            """, (user_id, category, month, year))
            conn.commit()

            print(f"Deleted category '{category}' for {month} {year}")
        finally:
            if conn:
                conn.close()