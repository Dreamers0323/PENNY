#!/usr/bin/env python3
"""
Test database connections for all modules
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.db_helper import get_db_connection

def test_accounts_operations():
    """Test typical account operations"""
    print("Testing accounts operations...")
    start = time.time()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test account queries
        cursor.execute("SELECT COUNT(*) FROM accounts")
        count = cursor.fetchone()[0]
        print(f"  Account count query: {count} accounts ({time.time() - start:.2f}s)")
        
        # Test account fetch for user
        start2 = time.time()
        cursor.execute("SELECT * FROM accounts WHERE user_id = ? LIMIT 5", ("1",))
        accounts = cursor.fetchall()
        print(f"  User accounts query: {len(accounts)} accounts ({time.time() - start2:.2f}s)")
        
        # Test transaction query
        start3 = time.time()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        trans_count = cursor.fetchone()[0]
        print(f"  Transaction count query: {trans_count} transactions ({time.time() - start3:.2f}s)")
        
        conn.close()
        total_time = time.time() - start
        print(f"  Total accounts test time: {total_time:.2f}s")
        
        if total_time > 5:
            print("  WARNING: Account operations are slow!")
            
    except Exception as e:
        print(f"  ERROR in accounts operations: {e}")

def test_budget_operations():
    """Test typical budget operations"""
    print("Testing budget operations...")
    start = time.time()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test budget queries
        cursor.execute("SELECT COUNT(*) FROM budget")
        count = cursor.fetchone()[0]
        print(f"  Budget count query: {count} budgets ({time.time() - start:.2f}s)")
        
        # Test budget fetch for user
        start2 = time.time()
        cursor.execute("SELECT * FROM budget WHERE user_id = ? LIMIT 5", ("1",))
        budgets = cursor.fetchall()
        print(f"  User budgets query: {len(budgets)} budgets ({time.time() - start2:.2f}s)")
        
        conn.close()
        total_time = time.time() - start
        print(f"  Total budget test time: {total_time:.2f}s")
        
        if total_time > 5:
            print("  WARNING: Budget operations are slow!")
            
    except Exception as e:
        print(f"  ERROR in budget operations: {e}")

def test_connection_pool():
    """Test multiple simultaneous connections"""
    print("Testing connection pool...")
    start = time.time()
    
    try:
        connections = []
        for i in range(5):
            conn = get_db_connection()
            connections.append(conn)
            
        print(f"  Created 5 connections in {time.time() - start:.2f}s")
        
        # Close all connections
        for conn in connections:
            conn.close()
            
        print("  All connections closed successfully")
        
    except Exception as e:
        print(f"  ERROR in connection pool test: {e}")

if __name__ == "__main__":
    print("=== DATABASE PERFORMANCE TEST ===")
    test_accounts_operations()
    print()
    test_budget_operations()
    print()
    test_connection_pool()
    print("=== TEST COMPLETE ===")