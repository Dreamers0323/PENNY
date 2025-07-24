# app.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user.repositories.sqllite_user_repo import SQLiteUserRepository
from user.services.AuthenticationSer import AuthenticationService
from user.services.RegistrationService import RegistrationService
from user.session import Session
from account.account_cli import launch_account_cli
from database.init_db import init_database
init_database()  # Ensures 'users' table exists before running app

def register_user():
    print("📝 Register New User")
    username = input("👤 Username (Employees start with ENTK): ")
    email = input("📧 Email: ")
    password = input("🔑 Password: ")
    role = input("🎭 Role (employee/customer): ").lower()

    try:
        reg_service = RegistrationService(SQLiteUserRepository("centralized.db"))
        reg_service.register(username, email, password, role)
        print("✅ Registration successful! You can now log in.")
    except ValueError as e:
        print(f"❌ Registration failed: {str(e)}")

def login_user():
    print("🔐 Login to Penny")
    email = input("📧 Email: ")
    password = input("🔑 Password: ")

    auth_service = AuthenticationService(SQLiteUserRepository("centralized.db"))

    try:
        user_id = auth_service.login(email, password)
        print("✅ Login successful!")
        return user_id  # Return only ID for session use
    except ValueError as e:
        print(f"❌ {str(e)}")
        return None

def main_menu():
    while True:
        current_user_id = Session.get("current_user_id")

        print("\n📱 Penny Main Menu")
        print("1. Account")
        print("2. Loan")
        print("3. Purchases")
        print("4. Logout")
        choice = input("Choose an option: ")

        if choice == "1":
            launch_account_cli(current_user_id)
        elif choice == "2":
            print("🔧 Loan module coming soon...")
        elif choice == "3":
            print("🔧 Purchase module coming soon...")
        elif choice == "4":
            print("👋 Logged out.")
            Session.clear()
            break
        else:
            print("❌ Invalid option.")

if __name__ == "__main__":
    print("🚀 Welcome to Penny!")

    while True:
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")
        option = input("Choose an option: ")

        if option == "1":
            user_id = login_user()
            if user_id:
                Session.set("current_user_id", user_id)
                main_menu()
        elif option == "2":
            register_user()
        elif option == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")
