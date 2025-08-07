# loan/loan_cli.py

from .loan_service import LoanService
from .models import LoanType
from datetime import datetime

loan_service = LoanService()

def display_menu():
    print("\n=== Penny Loan System ===")
    print("1. Apply for a loan")
    print("2. Approve a loan")
    print("3. Make a repayment")
    print("4. View My loans")
    print("5. Exit")

def choose_loan_type():
    print("\nChoose Loan Type:")
    for i, lt in enumerate(LoanType, 1):
        print(f"{i}. {lt.value}")
    
    while True:
        choice = input("Enter choice (1-3): ")
        if choice.isdigit() and 1 <= int(choice) <= len(LoanType):
            return list(LoanType)[int(choice)-1].value
        print(f"Invalid choice. Please enter 1-{len(LoanType)}")

def launch_loan_cli(user_id: str):
    while True:
        display_menu()
        option = input("Select an option: ")

        if option == "1":
            print("\n--- Apply for Loan ---")
            principal = float(input("Enter Principal Amount: "))
            interest_rate = float(input("Enter Interest Rate (%): "))
            term = int(input("Enter Loan Term (in months): "))
            loan_type = choose_loan_type()
            reason = input("Enter Loan Reason (optional): ")

            # Only call this once - the service handles ID generation
            loan = loan_service.apply_for_loan(
                user_id=user_id,
                principal=principal,
                interest_rate=interest_rate,
                term_months=term,
                loan_type=loan_type,
                reason=reason
            )
            print(f"\n✅ Loan applied successfully! ID: {loan.id}")

        elif option == "2":
            print("\n--- Approve Loan ---")
            loan_id = int(input("Enter Loan ID to approve: "))  # Convert to int
            success = loan_service.approve_loan(loan_id)
            if success:
                print(f"✅ Loan {loan_id} approved.")
            else:
                print("❌ Loan not found or already approved.")

        elif option == "3":
            print("\n--- Make Repayment ---")
            loan_id = int(input("Enter Loan ID: "))  # Convert to int
            amount = float(input("Enter Repayment Amount: "))
            
            success = loan_service.make_repayment(loan_id, amount)
            if success:
                print("✅ Repayment recorded.")
            else:
                print("❌ Failed to make repayment. Loan may not exist or is not approved.")

        elif option == "4":
            print("\n--- View User's Loans ---")
            loans = loan_service.get_loans_by_user(user_id)

            if not loans:
                print("No loans found for this user.")
            else:
                for loan in loans:
                    print(f"\n📄 Loan ID: {loan.id}")
                    print(f"Type: {loan.loan_type}")
                    print(f"Status: {loan.status}")
                    print(f"Principal: {loan.principal}")
                    print(f"Interest Rate: {loan.interest_rate}%")
                    print(f"Term: {loan.term_months} months")
                    print(f"Total Repayment: {loan.total_repayment:.2f}")
                    print(f"Monthly Payment: {loan.monthly_payment:.2f}")
                    print(f"Balance Remaining: {loan.balance_remaining:.2f}")

        elif option == "5":
            print("Exiting Penny Loan System.")
            break

        else:
            print("Invalid option. Please try again.")