# purchases/purchase_manager.py

from database.db import get_connection

def record_purchase(user_id, item, amount, date, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO purchases (user_id, item, amount, date, category)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, item, amount, date, category))
    conn.commit()
    conn.close()

def get_purchases_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM purchases WHERE user_id = ?
    """, (user_id,))
    purchases = cursor.fetchall()
    conn.close()
    return purchases
