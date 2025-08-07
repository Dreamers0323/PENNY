# loan/loan_manager.py
# this module manages loan applications and retrievals
# loan/loan_manager.py
from database.db import get_connection

def ensure_loans_table_exists():
    """Ensure the loans table exists before any operations"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            principal REAL,
            interest_rate REAL,
            term_months INTEGER,
            loan_type TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()

def apply_loan(user_id, principal, interest_rate, term_months, loan_type):
    # Ensure table exists before inserting
    ensure_loans_table_exists()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO loans (user_id, principal, interest_rate, term_months, loan_type, status)
        VALUES (?, ?, ?, ?, ?, 'pending')
    """, (user_id, principal, interest_rate, term_months, loan_type))
    
    conn.commit()
    conn.close()
    print("✅ Loan application submitted successfully!")

def get_loans_by_user(user_id):
    # Ensure table exists before querying
    ensure_loans_table_exists()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM loans WHERE user_id = ?
    """, (user_id,))
    
    loans = cursor.fetchall()
    conn.close()
    return loans