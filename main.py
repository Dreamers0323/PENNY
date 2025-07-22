# main.py

from database.db import initialize_database
from user.user_manager import register_user, login_user
from account.account_manager import create_account
from loan.loan_manager import apply_loan
from purchases.purchase_manager import record_purchase

def main():
    initialize_database()

    # Example flow
    register_user("Taizya", "taizya@email.com", "secure123", "customer")
    user = login_user("taizya@email.com", "secure123")
    
    if user:
        print("User logged in:", user)
        user_id = user[0]

        create_account(user_id, "savings")
        apply_loan(user_id, 5000, 0.05, 12, "full")
        record_purchase(user_id, "Laptop", 1000, "2025-07-22", "Tech")
    else:
        print("Login failed")

if __name__ == "__main__":
    main()
