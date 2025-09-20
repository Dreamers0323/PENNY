#!/usr/bin/env python3
"""
Script to unlock a locked SQLite database
"""

import sys
import os
import sqlite3
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def unlock_database():
    """Attempt to unlock the database by forcing connections closed"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'penny.db')
    
    print("Attempting to unlock database...")
    
    try:
        # Try to open and immediately close a connection
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')  # Enable WAL mode
        conn.execute('SELECT 1')  # Simple test query
        conn.close()
        print("✓ Database is now accessible!")
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("Database is still locked. Trying additional methods...")
            
            # Method 2: Try with different connection parameters
            try:
                conn = sqlite3.connect(f"file:{db_path}?cache=shared&uri=true", timeout=30.0)
                conn.execute('PRAGMA busy_timeout=30000')
                conn.execute('SELECT 1')
                conn.close()
                print("✓ Database unlocked using shared cache method!")
                return True
            except Exception as e2:
                print(f"Shared cache method failed: {e2}")
            
            print("❌ Database is still locked. You may need to:")
            print("1. Stop your Flask application completely")
            print("2. Wait a few seconds")
            print("3. Restart the application")
            return False
        else:
            print(f"Different database error: {e}")
            return False
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def check_database_status():
    """Check if database is accessible"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'penny.db')
    
    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✓ Database is accessible! Found {count} users.")
        return True
    except Exception as e:
        print(f"❌ Database is not accessible: {e}")
        return False

if __name__ == "__main__":
    print("=== DATABASE UNLOCK UTILITY ===")
    
    if check_database_status():
        print("Database is already working fine!")
    else:
        unlock_database()
        time.sleep(2)
        check_database_status()