# app.py

from database.db import initialize_database
from user.user_manager import register_user, login_user
from account.account_manager import create_account, get_account_by_user
from loan.loan_manager import apply_loan, get_loans_by_user
from purchases.purchase_manager import record_purchase, get_purchases_by_user

def handle_register():
    print("\n-- Register --")
    name = input("Name: ")
    email = input("Email: ")
    password = input("Password: ")
    user_type = input("User Type (customer/employee): ").lower()

    if user_type not in ["customer", "employee"]:
        print("❌ Invalid user type!")
        return None

    register_user(name, email, password, user_type)
    print("✅ Registration successful!")

def handle_login():
    print("\n-- Login --")
    email = input("Email: ")
    password = input("Password: ")

    user = login_user(email, password)
    if user:
        print(f"✅ Logged in as {user[1]}")
        return user
    else:
        print("❌ Login failed.")
        return None

def handle_account(user_id):
    print("\n-- Account Menu --")
    account = get_account_by_user(user_id)
    if account:
        print(f"📘 Account found: Type: {account[2]}, Balance: {account[3]}")
    else:
        acc_type = input("No account found. Enter account type (e.g. savings, current): ")
        create_account(user_id, acc_type)
        print("✅ Account created.")

def handle_loan(user_id):
    print("\n-- Loan Menu --")
    choice = input("1. Apply for Loan\n2. View Loans\nChoose: ")
    if choice == "1":
        principal = float(input("Enter principal amount: "))
        rate = float(input("Enter interest rate (e.g. 0.05): "))
        term = int(input("Enter loan term in months: "))
        ltype = input("Loan type (full, percentage, collateral): ")
        apply_loan(user_id, principal, rate, term, ltype)
        print("✅ Loan application submitted.")
    elif choice == "2":
        loans = get_loans_by_user(user_id)
        if loans:
            print("📄 Your Loans:")
            for loan in loans:
                print(f"- Amount: {loan[2]}, Rate: {loan[3]}, Term: {loan[4]} months, Status: {loan[6]}")
        else:
            print("ℹ️ No loans found.")

def handle_purchase(user_id):
    print("\n-- Purchase Menu --")
    choice = input("1. Record Purchase\n2. View Purchases\nChoose: ")
    if choice == "1":
        item = input("Item name: ")
        amount = float(input("Amount: "))
        date = input("Date (YYYY-MM-DD): ")
        category = input("Category (e.g. groceries, tech): ")
        record_purchase(user_id, item, amount, date, category)
        print("✅ Purchase recorded.")
    elif choice == "2":
        purchases = get_purchases_by_user(user_id)
        if purchases:
            print("🧾 Your Purchases:")
            for p in purchases:
                print(f"- {p[2]}: K{p[3]} on {p[4]} ({p[5]})")
        else:
            print("ℹ️ No purchases found.")

def main_menu(user):
    while True:
        print("\n📱 Penny Main Menu")
        print("1. Account")
        print("2. Loan")
        print("3. Purchases")
        print("4. Logout")
        choice = input("Choose an option: ")

        if choice == "1":
            handle_account(user[0])
        elif choice == "2":
            handle_loan(user[0])
        elif choice == "3":
            handle_purchase(user[0])
        elif choice == "4":
            print("👋 Logged out.")
            break
        else:
            print("❌ Invalid option.")

def main():
    initialize_database()
    print("🔐 Welcome to Penny")

    while True:
        print("\n1. Login\n2. Register\n3. Exit")
        option = input("Choose an option: ")

        if option == "1":
            user = handle_login()
            if user:
                main_menu(user)
        elif option == "2":
            handle_register()
        elif option == "3":
            print("👋 Goodbye.")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
