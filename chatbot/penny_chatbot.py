# chatbot/penny_chatbot.py
# this module implements the Penny chatbot for user interactions
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_connection
from account.account_service import AccountService



class PennyChatbot:
    def __init__(self, user_id):
        self.user_id = user_id
        self.account_service = AccountService()

    def start_chat(self):
        print("🤖 Penny: Hi! You can ask me about your balance, account summary, or transactions.")
        while True:
            user_input = input("You: ").lower()

            if "balance" in user_input:
                accounts = self.account_service.get_accounts_by_user(self.user_id)
                if accounts:
                    for acc in accounts:
                        print(f"🤖 Penny: {acc['account_type']} (ID: {acc['account_id']}) → Balance: {acc['balance']} ZMW")
                else:
                    print("🤖 Penny: I couldn’t find any accounts for you.")

            elif "summary" in user_input or "account" in user_input:
                accounts = self.account_service.get_accounts_by_user(self.user_id)
                if accounts:
                    for acc in accounts:
                        print(f"🤖 Penny: Account {acc['account_id']} | Type: {acc['account_type']} | Balance: {acc['balance']} ZMW | Active: {acc['active']}")
                else:
                    print("🤖 Penny: No accounts found.")

            elif "transactions" in user_input:
                accounts = self.account_service.get_accounts_by_user(self.user_id)
                if accounts:
                    for acc in accounts:
                        txns = self.account_service.get_transaction_history(acc['account_id'])
                        print(f"📜 Transactions for {acc['account_type']} ({acc['account_id']}):")
                        if txns:
                            for txn in txns:
                                print(f"   - {txn[0]} of {txn[1]} ZMW at {txn[2]}")
                        else:
                            print("   No transactions found.")
                else:
                    print("🤖 Penny: No accounts found.")

            elif user_input in ["exit", "quit", "bye"]:
                print("🤖 Penny: Bye! 👋")
                break

            else:
                print("🤖 Penny: I’m still learning. Try asking about balance, summary, or transactions.")
