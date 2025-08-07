# loan/loan_cli.py

from loan.loan_manager import apply_loan, get_loans_by_user
from enum import Enum

class LoanType(Enum):
    FULL = "Full"
    INSTALLMENT = "Installment"
    COLLATERAL = "Collateral"

def launch_loan_cli(user_id):
    while True:
        print("\n💰 Loan Menu")
        print("1. Apply for Loan")
        print("2. View My Loans")
        print("3. Back to Main Menu")
        choice = input("Choose an option: ")

        if choice == "1":
            apply_for_loan_cli(user_id)
        elif choice == "2":
            view_loans_cli(user_id)
        elif choice == "3":
            break
        else:
            print("❌ Invalid option.")

def apply_for_loan_cli(user_id):
    print("\n📝 Apply for Loan")
    try:
        principal = float(input("💵 Principal amount: "))
        interest_rate = float(input("📈 Interest rate (%): "))
        term_months = int(input("📆 Loan term (months): "))
        print("📑 Loan Types: Full, Installment, Collateral")
        loan_type = input("🔍 Loan type: ").capitalize()

        if loan_type not in [lt.value for lt in LoanType]:
            print("❌ Invalid loan type.")
            return

        apply_loan(user_id, principal, interest_rate, term_months, loan_type)
        print("✅ Loan application submitted.")
    except ValueError:
        print("❌ Invalid input. Please enter numbers where required.")

def view_loans_cli(user_id):
    print("\n📋 Your Loans")
    loans = get_loans_by_user(user_id)
    if not loans:
        print("📭 No loans found.")
        return

    for loan in loans:
        print(f"📌 Loan ID: {loan[0]}, Principal: {loan[2]}, Rate: {loan[3]}%, Term: {loan[4]} months, Type: {loan[5]}, Status: {loan[6]}")
