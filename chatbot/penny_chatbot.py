# chatbot/penny_chatbot.py
# Penny chatbot for user interactions (Accounts + Purchases)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from account.account_service import AccountService
from purchases.purchase_service import PurchaseService


class PennyChatbot:
    def __init__(self, user_id):
        self.user_id = user_id
        self.account_service = AccountService()
        self.purchase_service = PurchaseService(user_id)

    def start_chat(self):
        print("🤖 Penny: Hi! You can ask me about:")
        print("  💰 your balance, account summary, or transactions")
        print("  📊 budgets and savings goals,")
        print("Type 'exit', 'quit' or 'bye' to end the chat.")

        while True:
            user_input = input("You: ").lower()

            # === ACCOUNT FEATURES ===
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
                        print(f"🤖 Penny: Account {acc['account_id']} | "
                              f"Type: {acc['account_type']} | "
                              f"Balance: {acc['balance']} ZMW | "
                              f"Active: {acc['active']}")
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

            # === PURCHASE FEATURES ===
            elif "set budget" in user_input:
                category = input("📂 Enter category: ")
                amount = float(input("💵 Enter amount: "))
                self.purchase_service.set_budget_category(category, amount)
                print(f"🤖 Penny: Budget set → {category}: {amount} ZMW")

            elif "budget summary" in user_input or "my budgets" in user_input:
                self.purchase_service.get_budget_summary()

            elif "set goal" in user_input:
                name = input("🏁 Goal name: ")
                target = float(input("💵 Target amount: "))
                self.purchase_service.add_savings_goal(name, target)
                print(f"🤖 Penny: Goal '{name}' set with target K{target:,.2f}")

            elif "goals" in user_input:
                goals = self.purchase_service.get_savings_goals()
                if goals:
                    print("🤖 Penny: Here are your savings goals:")
                    for g_name, t_amt, s_amt in goals:
                        percent = (s_amt / t_amt * 100) if t_amt > 0 else 0
                        print(f"   🎯 {g_name}: {s_amt}/{t_amt} (📊 {percent:.1f}%)")
                else:
                    print("🤖 Penny: You don’t have any savings goals yet.")

            elif "add to goal" in user_input:
                name = input("🏁 Which goal? ")
                amount = float(input("💵 Amount to add: "))
                self.purchase_service.update_savings_progress(name, amount)
                print(f"🤖 Penny: Added K{amount} to goal '{name}'")

            elif "delete goal" in user_input:
                name = input("❌ Goal to delete: ")
                self.purchase_service.delete_savings_goal(name)
                print(f"🤖 Penny: Goal '{name}' deleted.")

            elif "expenses" in user_input:
                expenses = self.purchase_service.get_expenses()
                if expenses:
                    print("🤖 Penny: Here are your expenses:")
                    for e_name, amount, date in expenses:
                        print(f"   🧾 {e_name}: {amount} ZMW on {date}")
                else:
                    print("🤖 Penny: You don’t have any expenses recorded yet.")

            # === EXIT ===
            elif user_input in ["exit", "quit", "bye"]:
                print("🤖 Penny: Bye! 👋")
                break

            else:
                print("🤖 Penny: I’m still learning. Try asking about balance, summary, transactions, budgets, goals, or expenses.")
