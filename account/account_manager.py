# account/account_manager.py
# This module handles account management operations such as creating accounts,
# retrieving accounts by user, and managing account transactions.

from database.db import get_connection

def create_account(user_id, account_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO accounts (user_id, account_type)
        VALUES (?, ?)
    """, (user_id, account_type))
    conn.commit()
    conn.close()

def get_account_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM accounts WHERE user_id = ?
    """, (user_id,))
    account = cursor.fetchone()
    conn.close()
    return account
