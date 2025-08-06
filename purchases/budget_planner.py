# budget_planner.py
# This module handles budget planning functionalities
# It allows users to set budgets, update them, and view summaries

from database.db import get_connection
from datetime import datetime

class BudgetPlanner:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
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

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS overall_budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                total_amount REAL,
                month TEXT,
                year INTEGER,
                created_at TEXT
            )
        """)
        self.conn.commit()

    def set_overall_budget(self, user_id, total_amount, month=None, year=None):
        month = month or datetime.now().strftime("%B")
        year = year or datetime.now().year
        created_at = datetime.now().isoformat()

        self.cursor.execute("""
            SELECT * FROM overall_budget WHERE user_id = ? AND month = ? AND year = ?
        """, (user_id, month, year))
        existing = self.cursor.fetchone()

        if existing:
            self.cursor.execute("""
                UPDATE overall_budget SET total_amount = ?, created_at = ? 
                WHERE user_id = ? AND month = ? AND year = ?
            """, (total_amount, created_at, user_id, month, year))
        else:
            self.cursor.execute("""
                INSERT INTO overall_budget (user_id, total_amount, month, year, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, total_amount, month, year, created_at))
        
        self.conn.commit()
        print(f"✅ Overall budget of K{total_amount} set for {month}, {year}")

    def set_budget(self, user_id, category, amount, month=None, year=None):
        month = month or datetime.now().strftime("%B")
        year = year or datetime.now().year
        created_at = datetime.now().isoformat()

        self.cursor.execute("""
            SELECT * FROM budget WHERE user_id = ? AND category = ? AND month = ? AND year = ?
        """, (user_id, category, month, year))

        if self.cursor.fetchone():
            self.update_budget(user_id, category, amount, month, year)
            return

        self.cursor.execute("""
            INSERT INTO budget (user_id, category, amount, month, year, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, category, amount, month, year, created_at))
        self.conn.commit()

        print(f"✅ Budget set: {category} - K{amount} for {month}, {year}")
        self.get_budget_summary(user_id, month, year)

    def update_budget(self, user_id, category, new_amount, month=None, year=None):
        month = month or datetime.now().strftime("%B")
        year = year or datetime.now().year

        self.cursor.execute("""
            UPDATE budget
            SET amount = ?
            WHERE user_id = ? AND category = ? AND month = ? AND year = ?
        """, (new_amount, user_id, category, month, year))
        self.conn.commit()

        print(f"🔄 Updated {category} budget to K{new_amount} for {month}, {year}")
        self.get_budget_summary(user_id, month, year)

    def get_budgets(self, user_id, month=None, year=None):
        month = month or datetime.now().strftime("%B")
        year = year or datetime.now().year

        self.cursor.execute("""
            SELECT category, amount FROM budget
            WHERE user_id = ? AND month = ? AND year = ?
        """, (user_id, month, year))

        budgets = self.cursor.fetchall()
        if budgets:
            print(f"\n📊 Budgets for {month} {year}:")
            for cat, amt in budgets:
                print(f"- {cat}: K{amt}")
        else:
            print(f"\n⚠️ No budgets found for {month} {year}.")

    def get_budget_summary(self, user_id, month=None, year=None):
        month = month or datetime.now().strftime("%B")
        year = year or datetime.now().year

        self.cursor.execute("""
            SELECT total_amount FROM overall_budget
            WHERE user_id = ? AND month = ? AND year = ?
        """, (user_id, month, year))
        total_budget = self.cursor.fetchone()

        if not total_budget:
            print(f"\n⚠️ You have not set an overall budget for {month} {year}.")
            return

        total_budget = total_budget[0]

        self.cursor.execute("""
            SELECT SUM(amount) FROM budget
            WHERE user_id = ? AND month = ? AND year = ?
        """, (user_id, month, year))

        total_spent = self.cursor.fetchone()[0] or 0.0
        remaining = total_budget - total_spent

        print(f"\n💰 Budget Summary for {month} {year}")
        print(f"- Overall Amount: K{total_budget}")
        print(f"- Total Budgeted (Expenses): K{total_spent}")
        print(f"- Amount Remaining (Can be saved): K{remaining}")

    def delete_budget_category(self, user_id, category, month=None, year=None):
        month = month or datetime.now().strftime("%B")
        year = year or datetime.now().year

        self.cursor.execute("""
            DELETE FROM budget
            WHERE user_id = ? AND category = ? AND month = ? AND year = ?
        """, (user_id, category, month, year))
        self.conn.commit()

        print(f"🗑️ Deleted category '{category}' for {month} {year}")
        self.get_budget_summary(user_id, month, year)

    def close(self):
        self.conn.close()
