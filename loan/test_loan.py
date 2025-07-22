# loan/test_loan.py
from loan_service import LoanService
from models import LoanType

loan_service = LoanService()

def display_menu():
    print("\n=== Penny Loan System ===")
    print("1. Apply for a loan")
    print("2. Approve a loan")
    print("3. Make a repayment")
    print("4. View user's loans")
    print("5. Exit")

def choose_loan_type():
    print("\nChoose Loan Type:")
    for i, lt in enumerate(LoanType, 1):
        print(f"{i}. {lt.value}")
    choice = int(input("Enter choice: "))
    return list(LoanType)[choice - 1]

while True:
    display_menu()
    option = input("Select an option: ")

    if option == "1":
        print("\n--- Apply for Loan ---")
        loan_id = input("Enter Loan ID: ")
        user_id = input("Enter User ID: ")
        principal = float(input("Enter Principal Amount: "))
        interest_rate = float(input("Enter Interest Rate (%): "))
        term = int(input("Enter Loan Term (in months): "))
        loan_type = choose_loan_type()
        reason = input("Enter Reason for Loan: ")

        loan = loan_service.apply_for_loan(
            loan_id, user_id, principal, interest_rate, term, loan_type, reason
        )

        print(f"\nLoan Applied:\n- ID: {loan.loan_id}\n- Type: {loan.loan_type.value}\n- Monthly Payment: {loan.calculate_monthly_payment():.2f}\n- Status: {loan.status.value}")

    elif option == "2":
        print("\n--- Approve Loan ---")
        loan_id = input("Enter Loan ID to approve: ")
        loan = loan_service.approve_loan(loan_id)
        if loan:
            print(f"Loan {loan_id} approved. Status: {loan.status.value}")
        else:
            print("Loan not found.")

    elif option == "3":
        print("\n--- Make Repayment ---")
        loan_id = input("Enter Loan ID: ")
        amount = float(input("Enter Repayment Amount: "))
        repayment = loan_service.make_repayment(loan_id, amount)
        if repayment:
            loan = loan_service._find_loan(loan_id)
            print(f"Repayment successful! Remaining balance: {loan.get_balance_remaining():.2f}")
            print(f"Loan Status: {loan.status.value}")
        else:
            print("Loan not found or not approved.")

    elif option == "4":
        print("\n--- View User's Loans ---")
        user_id = input("Enter User ID: ")
        loans = loan_service.get_loans_by_user(user_id)
        if not loans:
            print("No loans found for this user.")
        else:
            for loan in loans:
                print(f"\nLoan ID: {loan.loan_id}")
                print(f"Type: {loan.loan_type.value}")
                print(f"Status: {loan.status.value}")
                print(f"Total Amount: {loan.calculate_total_amount():.2f}")
                print(f"Monthly Payment: {loan.calculate_monthly_payment():.2f}")
                print(f"Balance Remaining: {loan.get_balance_remaining():.2f}")
                print("Repayments:")
                for r in loan.repayments:
                    print(f" - {r.amount} on {r.payment_date}")

    elif option == "5":
        print("Exiting Penny Loan System.")
        break

    else:
        print("Invalid option. Please try again.")
