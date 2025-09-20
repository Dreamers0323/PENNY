#!/usr/bin/env python3
"""
Fix database schema after failed migration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db_helper import get_db_connection

def fix_database_schema():
    """Fix the database schema after failed migration"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Fixing database schema...")
        
        # 1. First, check the current state
        cursor.execute("PRAGMA table_info(loans)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns in loans table: {columns}")
        
        # 2. Add application_date column with a simple default first
        if 'application_date' not in columns:
            try:
                cursor.execute("ALTER TABLE loans ADD COLUMN application_date TEXT DEFAULT ''")
                print("✓ Added application_date column with empty default")
            except Exception as e:
                print(f"✗ Error adding application_date: {e}")
        
        # 3. Update the application_date for existing records
        try:
            cursor.execute("UPDATE loans SET application_date = datetime('now') WHERE application_date = '' OR application_date IS NULL")
            print("✓ Updated application_date for existing records")
        except Exception as e:
            print(f"✗ Error updating application_date: {e}")
        
        # 4. Check if we need to add any other missing columns
        columns_to_check = ['reason', 'monthly_payment', 'total_repayment', 'balance_remaining']
        for column in columns_to_check:
            if column not in columns:
                try:
                    if column == 'reason':
                        cursor.execute(f"ALTER TABLE loans ADD COLUMN {column} TEXT DEFAULT ''")
                    else:
                        cursor.execute(f"ALTER TABLE loans ADD COLUMN {column} REAL DEFAULT 0")
                    print(f"✓ Added {column} column")
                except Exception as e:
                    print(f"✗ Error adding {column}: {e}")
        
        # 5. Set balance_remaining for existing loans
        try:
            cursor.execute("UPDATE loans SET balance_remaining = principal WHERE balance_remaining IS NULL OR balance_remaining = 0")
            print("✓ Set balance_remaining for existing loans")
        except Exception as e:
            print(f"✗ Error setting balance_remaining: {e}")
        
        conn.commit()
        print("✓ Database schema fix completed!")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(loans)")
        new_columns = [col[1] for col in cursor.fetchall()]
        print(f"Final columns: {new_columns}")
        
        # Show some sample data
        cursor.execute("SELECT id, user_id, principal, balance_remaining, application_date FROM loans LIMIT 5")
        sample_data = cursor.fetchall()
        print("Sample loan data:")
        for row in sample_data:
            print(f"  Loan {row[0]}: User {row[1]}, Principal: {row[2]}, Balance: {row[3]}, Date: {row[4]}")
        
    except Exception as e:
        print(f"✗ Error during schema fix: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Starting database schema fix...")
    fix_database_schema()
    print("Schema fix completed!")