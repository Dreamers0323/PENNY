# account/account_service.py
import sqlite3
import uuid
from datetime import datetime

from .exceptions import AccountNotFoundError, InsufficientFundsError, InactiveAccountError
from user.session import Session  # Reuse the session module

class AccountService:
    def __init__(self):
        self.conn = sqlite3.connect("central_database.db")
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                account_type TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def create_account(self, user_id: str, account_type: str):
        if account_type not in ["Savings", "Checking"]:
            raise ValueError("Invalid account type.")

        account_id = str(uuid.uuid4())
        self.cursor.execute('''
            INSERT INTO accounts (account_id, user_id, account_type, balance, active)
            VALUES (?, ?, ?, ?, ?)
        ''', (account_id, user_id, account_type, 0.0, 1))
        self.conn.commit()

        return {"account_id": account_id, "account_type": account_type, "balance": 0.0}

    def deposit(self, account_id: str, amount: float):
        account = self._get_active_account(account_id)
        new_balance = account["balance"] + amount

        self.cursor.execute('''
            UPDATE accounts SET balance = ? WHERE account_id = ?
        ''', (new_balance, account_id))
        self._record_transaction(account_id, amount, "deposit")
        self.conn.commit()

        return new_balance

    def withdraw(self, account_id: str, amount: float):
        account = self._get_active_account(account_id)
        if account["balance"] < amount:
            raise InsufficientFundsError("Insufficient funds.")

        new_balance = account["balance"] - amount

        self.cursor.execute('''
            UPDATE accounts SET balance = ? WHERE account_id = ?
        ''', (new_balance, account_id))
        self._record_transaction(account_id, amount, "withdraw")
        self.conn.commit()

        return new_balance

    def transfer_funds(self, from_id: str, to_id: str, amount: float):
        from_acc = self._get_active_account(from_id)
        to_acc = self._get_active_account(to_id)

        if from_acc["balance"] < amount:
            raise InsufficientFundsError("Insufficient funds for transfer.")

        new_from_balance = from_acc["balance"] - amount
        new_to_balance = to_acc["balance"] + amount

        self.cursor.execute('UPDATE accounts SET balance = ? WHERE account_id = ?', (new_from_balance, from_id))
        self.cursor.execute('UPDATE accounts SET balance = ? WHERE account_id = ?', (new_to_balance, to_id))

        self._record_transaction(from_id, amount, "transfer_out")
        self._record_transaction(to_id, amount, "transfer_in")
        self.conn.commit()

        return new_from_balance, new_to_balance

    def check_funds(self, account_id: str):
        account = self._get_account(account_id)
        return account["balance"]

    def update_account(self, account_id: str, **kwargs):
        for key, val in kwargs.items():
            self.cursor.execute(f'''
                UPDATE accounts SET {key} = ? WHERE account_id = ?
            ''', (val, account_id))
        self.conn.commit()

        return self._get_account(account_id)

    def _record_transaction(self, account_id: str, amount: float, transaction_type: str):
        tx_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        self.cursor.execute('''
            INSERT INTO transactions (transaction_id, account_id, amount, transaction_type, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (tx_id, account_id, amount, transaction_type, timestamp))

    def _get_account(self, account_id: str):
        self.cursor.execute('SELECT * FROM accounts WHERE account_id = ?', (account_id,))
        row = self.cursor.fetchone()
        if not row:
            raise AccountNotFoundError("Account not found.")
        return {
            "account_id": row[0],
            "user_id": row[1],
            "account_type": row[2],
            "balance": row[3],
            "active": bool(row[4])
        }

    def _get_active_account(self, account_id: str):
        acc = self._get_account(account_id)
        if not acc["active"]:
            raise InactiveAccountError("Account is inactive.")
        return acc

    def get_transaction_history(self, account_id: str):
        self.cursor.execute('''
            SELECT transaction_type, amount, timestamp FROM transactions
            WHERE account_id = ? ORDER BY timestamp DESC
        ''', (account_id,))
        return self.cursor.fetchall()
