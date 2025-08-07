# loan/loan_manager.py
# this module manages loan applications and retrievals
from database.db import get_connection
from datetime import datetime

def ensure_loans_table_exists():
    """Ensure the loans and repayments tables exist with all required fields"""
    conn = get_connection('penny.db')  # Specify the database name
    cursor = conn.cursor()
    
    # Loans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            principal REAL NOT NULL,
            interest_rate REAL NOT NULL,
            term_months INTEGER NOT NULL,
            loan_type TEXT NOT NULL,
            reason TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            application_date TEXT DEFAULT CURRENT_TIMESTAMP,
            monthly_payment REAL,
            total_repayment REAL DEFAULT 0,
            balance_remaining REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    # Repayments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repayments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(loan_id) REFERENCES loans(id)
        )
    """)
    
    conn.commit()
    conn.close()

def apply_loan(user_id, principal, interest_rate, term_months, loan_type, reason=""):
    """Apply for a loan with all necessary fields"""
    ensure_loans_table_exists()
    
    # Calculate monthly payment
    monthly_rate = interest_rate / 100 / 12
    monthly_payment = (principal * monthly_rate) / (1 - (1 + monthly_rate) ** -term_months)
    
    conn = get_connection('penny.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO loans 
        (user_id, principal, interest_rate, term_months, loan_type, reason, 
         status, monthly_payment, balance_remaining)
        VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
    """, (user_id, principal, interest_rate, term_months, loan_type, reason,
          monthly_payment, principal))
    
    loan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return loan_id

def get_loans_by_user(user_id):
    """Get all loans for a user with repayment calculations"""
    ensure_loans_table_exists()
    
    conn = get_connection('penny.db')
    cursor = conn.cursor()
    
def approve_loan_db(loan_id: int) -> bool:
    """Set loan status to 'approved'"""
    ensure_loans_table_exists()
    conn = get_connection('penny.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE loans SET status = 'approved' WHERE id = ?", (loan_id,))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def reject_loan_db(loan_id: int) -> bool:
    """Set loan status to 'rejected'"""
    ensure_loans_table_exists()
    conn = get_connection('penny.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE loans SET status = 'rejected' WHERE id = ?", (loan_id,))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def make_repayment_db(loan_id: int, amount: float) -> bool:
    """Add a repayment record and update balance_remaining"""
    ensure_loans_table_exists()
    conn = get_connection('penny.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO repayments (loan_id, amount) VALUES (?, ?)",
        (loan_id, amount)
    )
    # Update balance_remaining
    cursor.execute(
        "UPDATE loans SET balance_remaining = balance_remaining - ? WHERE id = ?",
        (amount, loan_id)
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def find_loan_db(loan_id: int):
    """Find a loan by its ID and return as dict"""
    ensure_loans_table_exists()
    conn = get_connection('penny.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        conn.close()
        return None
    # Get total repayment
    cursor.execute("SELECT SUM(amount) FROM repayments WHERE loan_id = ?", (loan_id,))
    total_repaid = cursor.fetchone()[0] or 0
    loan_dict = {
        'id': loan[0],
        'user_id': loan[1],
        'principal': loan[2],
        'interest_rate': loan[3],
        'term_months': loan[4],
        'loan_type': loan[5],
        'reason': loan[6],
        'status': loan[7],
        'application_date': loan[8],
        'monthly_payment': loan[9],
        'total_repayment': total_repaid,
        'balance_remaining': loan[10]
    }
    conn.close()
    return loan_dict

def get_loans_by_user(user_id):
    """Get all loans for a user with repayment calculations"""
    ensure_loans_table_exists()
    conn = get_connection('penny.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loans WHERE user_id = ?", (user_id,))
    loans = cursor.fetchall()
    loan_data = []
    for loan in loans:
        cursor.execute("SELECT SUM(amount) FROM repayments WHERE loan_id = ?", (loan[0],))
        total_repaid = cursor.fetchone()[0] or 0
        loan_data.append({
            'id': loan[0],
            'user_id': loan[1],
            'principal': loan[2],
            'interest_rate': loan[3],
            'term_months': loan[4],
            'loan_type': loan[5],
            'reason': loan[6],
            'status': loan[7],
            'application_date': loan[8],
            'monthly_payment': loan[9],
            'total_repayment': total_repaid,
            'balance_remaining': loan[10]
        })
    conn.close()
    return loan_data