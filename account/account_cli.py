# A simple command-line interface for managing Penny accounts.
# This module provides a CLI for the Penny account management system.
from account_service import AccountService, AccountNotFoundError, InsufficientFundsError

def main():
    service = AccountService()

    accounts = {}

    while True:
        print("\n--- Penny Account Module ---")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer Funds")
        print("5. Check Balance")
        print("6. View Transaction History")
        print("7. Update Account")
        print("8. Exit")
        
        choice = input("Select an option: ")

        try:
            if choice == "1":
                user_id = input("Enter user ID: ")
                acc_type = input("Enter account type (Savings/Checking): ")
                acc = service.create_account(user_id, acc_type)
                accounts[acc.account_id] = acc
                print(f"Account created! ID: {acc.account_id}")

            elif choice == "2":
                acc_id = input("Enter account ID: ")
                amt = float(input("Enter amount to deposit: "))
                bal = service.deposit(acc_id, amt)
                print(f"Deposit successful. New balance: {bal}")

            elif choice == "3":
                acc_id = input("Enter account ID: ")
                amt = float(input("Enter amount to withdraw: "))
                bal = service.withdraw(acc_id, amt)
                print(f"Withdrawal successful. New balance: {bal}")

            elif choice == "4":
                from_id = input("Enter your account ID: ")
                to_id = input("Enter recipient account ID: ")
                amt = float(input("Enter amount to transfer: "))
                from_bal, to_bal = service.transfer_funds(from_id, to_id, amt)
                print(f"Transfer complete. Your balance: {from_bal}, Recipient balance: {to_bal}")

            elif choice == "5":
                acc_id = input("Enter account ID: ")
                bal = service.check_funds(acc_id)
                print(f"Account balance: {bal}")

            elif choice == "6":
                acc_id = input("Enter account ID: ")
                txs = service.get_transaction_history(acc_id)
                for tx in txs:
                    print(f"{tx.timestamp}: {tx.transaction_type} {tx.amount}")

            elif choice == "7":
                acc_id = input("Enter account ID: ")
                key = input("Enter field to update (e.g., nickname): ")
                val = input(f"Enter new value for {key}: ")
                acc = service.update_account(acc_id, **{key: val})
                print(f"Account updated: {vars(acc)}")

            elif choice == "8":
                print("Goodbye!")
                break

            else:
                print("Invalid option.")

        except (AccountNotFoundError, InsufficientFundsError, ValueError) as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
