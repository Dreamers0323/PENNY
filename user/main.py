from db import init_db
from repositories.sqllite_user_repo import SQLiteUserRepository
from services.RegistrationService import RegistrationService
from services.AuthenticationSer import AuthenticationService

def main():
    init_db()

    repo = SQLiteUserRepository()
    reg_service = RegistrationService(repo)
    auth_service = AuthenticationService(repo)

    while True:
        print("\n=== PENNY SYSTEM - USER MANAGEMENT ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option (1-3): ")

        if choice == "1":
            print("\n--- Register ---")
            username = input("Enter username: ")
            email = input("Enter email: ")
            password = input("Enter password: ")
            role = input("Enter role (customer/employee): ").lower()

            try:
                message = reg_service.register(username, email, password, role)
                print(f"✅ {message}")
            except ValueError as e:
                print(f"❌ Registration failed: {e}")

        elif choice == "2":
            print("\n--- Login ---")
            email = input("Enter email: ")
            password = input("Enter password: ")

            try:
                message = auth_service.login(email, password)
                print(f"✅ {message}")
            except ValueError as e:
                print(f"❌ Login failed: {e}")

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()