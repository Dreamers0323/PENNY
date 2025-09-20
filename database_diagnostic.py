#!/usr/bin/env python3
"""
Database diagnostic script to check what tables and columns exist
This will show you exactly what's in your database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db_helper import get_db_connection

def check_all_tables():
    """Check all tables and their columns in the database"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("=== DATABASE DIAGNOSTIC REPORT ===")
        print(f"Database has {len(tables)} tables:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n📋 TABLE: {table_name}")
            print("-" * 40)
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_text = " (PRIMARY KEY)" if pk else ""
                not_null_text = " NOT NULL" if not_null else ""
                default_text = f" DEFAULT {default_val}" if default_val else ""
                print(f"  ✓ {col_name}: {col_type}{not_null_text}{default_text}{pk_text}")
            
            # Count records
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  📊 Records: {count}")
            except Exception as e:
                print(f"  ⚠️  Could not count records: {e}")
        
        print("\n=== END DIAGNOSTIC REPORT ===")
        
    except Exception as e:
        print(f"Error during diagnostic: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_all_tables()