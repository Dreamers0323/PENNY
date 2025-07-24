# A simple command-line interface for managing Penny accounts.
# This module provides a CLI for the Penny account management system.
# account/account_cli.py

from user.session import Session
from account.account_service import AccountService
from .exceptions import AccountNotFoundError, InsufficientFundsError

def launch_account_cli(user_id=None):
    service = AccountService()
    
    # Use passed user_id or session
    if user_id is None:
        user_id = Session.get("current_user_id")
    
    if user_id is None:
        print("⚠️ No user is currently logged in. Please log in first.")
        return

    while True:
        print("\n--- Penny Account Module ---")
        print("1. Create Account")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer Funds")
        print("5. Check Balance")
        print("6. View Transaction History")
        print("7. Update Account")
        print("8. Back to Main Menu")

        choice = input("Select an option: ")

        try:
            if choice == "1":
                acc_type = input("Enter account type (Savings/Checking): ")
                acc = service.create_account(user_id, acc_type)
                print(f"✅ Account created! ID: {acc.account_id}")

            elif choice == "2":
                acc_id = input("Enter account ID: ")
                amt = float(input("Enter amount to deposit: "))
                bal = service.deposit(user_id, acc_id, amt)
                print(f"✅ Deposit successful. New balance: {bal}")

            elif choice == "3":
                acc_id = input("Enter account ID: ")
                amt = float(input("Enter amount to withdraw: "))
                bal = service.withdraw(user_id, acc_id, amt)
                print(f"✅ Withdrawal successful. New balance: {bal}")

            elif choice == "4":
                from_id = input("Enter your account ID: ")
                to_id = input("Enter recipient account ID: ")
                amt = float(input("Enter amount to transfer: "))
                from_bal, to_bal = service.transfer_funds(user_id, from_id, to_id, amt)
                print(f"✅ Transfer complete. Your balance: {from_bal}, Recipient balance: {to_bal}")

            elif choice == "5":
                acc_id = input("Enter account ID: ")
                bal = service.check_funds(user_id, acc_id)
                print(f"💰 Account balance: {bal}")

            elif choice == "6":
                acc_id = input("Enter account ID: ")
                txs = service.get_transaction_history(user_id, acc_id)
                if txs:
                    for tx in txs:
                        print(f"{tx.timestamp}: {tx.transaction_type} {tx.amount}")
                else:
                    print("📭 No transactions found.")

            elif choice == "7":
                acc_id = input("Enter account ID: ")
                key = input("Enter field to update (e.g., nickname): ")
                val = input(f"Enter new value for {key}: ")
                acc = service.update_account(user_id, acc_id, **{key: val})
                print(f"✅ Account updated: {vars(acc)}")

            elif choice == "8":
                print("🔙 Returning to main menu...")
                break

            else:
                print("❌ Invalid option.")

        except (AccountNotFoundError, InsufficientFundsError, ValueError) as e:
            print(f"⚠️ Error: {e}")
