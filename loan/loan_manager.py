# loan/loan_manager.py

from database.db import get_connection

def apply_loan(user_id, principal, interest_rate, term_months, loan_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO loans (user_id, principal, interest_rate, term_months, loan_type, status)
        VALUES (?, ?, ?, ?, ?, 'pending')
    """, (user_id, principal, interest_rate, term_months, loan_type))
    conn.commit()
    conn.close()

def get_loans_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM loans WHERE user_id = ?
    """, (user_id,))
    loans = cursor.fetchall()
    conn.close()
    return loans
