# chatbot/penny_chatbot.py
# Penny chatbot for user interactions (Accounts + Purchases)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from account.account_service import AccountService
from purchases.purchase_service import PurchaseService
from loan.loan_service import LoanService

class PennyChatbot:
    def __init__(self, user_id):
        self.user_id = user_id
        try:
            self.account_service = AccountService()
            self.purchase_service = PurchaseService(user_id)
            self.loan_service = LoanService()
        except Exception as e:
            print(f"Error initializing PennyChatbot services: {e}")
            raise

    def process_message(self, user_input):
        """Process user input and return a response string"""
        try:
            user_input = user_input.lower().strip()
            
            # Add debug logging
            print(f"Processing message: '{user_input}' for user {self.user_id}")
            
            # === HELP ===
            if "help" in user_input:
                return self._get_help_response()
            
            # === ACCOUNT FEATURES ===
            elif "balance" in user_input:
                return self._get_balance_response()
                
            elif "summary" in user_input or "account" in user_input:
                return self._get_account_summary_response()
                
            elif "transactions" in user_input or "history" in user_input:
                return self._get_transactions_response()
                
            # === PURCHASE FEATURES ===
            elif "set budget" in user_input:
                return "To set a budget, please use the 'Plans' section. I can help you view your current budgets though!"
                
            elif "budget" in user_input or "my budgets" in user_input:
                return self._get_budget_summary_response()
                
            elif "set goal" in user_input or "savings goal" in user_input:
                return "To set a savings goal, please use the 'Plans' section. I can show you your current goals!"
                
            elif "goal" in user_input or "savings" in user_input:
                return self._get_savings_goals_response()
                
            elif "expenses" in user_input:
                return self._get_expenses_response()
            
            elif "loan" in user_input:
                return self._get_loans_response()
                
            # === GREETINGS ===
            elif any(word in user_input for word in ["hello", "hi", "hey", "greetings"]):
                return "Hello! I'm Penny, your financial assistant. How can I help you today? You can ask me about your balance, accounts, transactions, budgets, or savings goals."
                
            elif any(word in user_input for word in ["problem", "issue", "complaint", "error", "not working"]):
                return self._get_complaint_response()

            # === DEFAULT RESPONSE ===
            else:
                return "I'm not sure I understand. Try asking me about your balance, accounts, transactions, budgets, or savings goals. Type 'help' to see what I can do."
                
        except Exception as e:
            print(f"Error in process_message: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."

    def _get_balance_response(self):
        """Get balance information"""
        try:
            accounts = self.account_service.get_accounts_by_user(self.user_id)
            if not accounts:
                return "You don't have any accounts yet. Please create an account first."
            
            response_parts = ["Here are your account balances:"]
            total_balance = 0
            
            for acc in accounts:
                response_parts.append(f"• {acc['account_type']}: ZMW {acc['balance']:.2f}")
                total_balance += acc['balance']
            
            response_parts.append(f"<br><strong>Total balance: ZMW {total_balance:.2f}</strong>")
            return "<br>".join(response_parts)
        except Exception as e:
            print(f"Error in _get_balance_response: {e}")
            return "I couldn't retrieve your balance information. Please try again later."

    def _get_account_summary_response(self):
        """Get account summary"""
        try:
            accounts = self.account_service.get_accounts_by_user(self.user_id)
            if not accounts:
                return "You don't have any accounts yet."
            
            response_parts = ["Here's your account summary:"]
            for acc in accounts:
                status = "Active" if acc['active'] else "Inactive"
                response_parts.append(f"• {acc['account_type']} ({acc['account_id'][-6:]}) - ZMW {acc['balance']:.2f} ({status})")
            
            return "<br>".join(response_parts)
        except Exception as e:
            print(f"Error in _get_account_summary_response: {e}")
            return "I couldn't retrieve your account information. Please try again later."

    def _get_transactions_response(self):
        """Get recent transactions"""
        try:
            accounts = self.account_service.get_accounts_by_user(self.user_id)
            if not accounts:
                return "You don't have any accounts yet."
            
            response_parts = ["Recent transactions:"]
            has_transactions = False
            
            for acc in accounts:
                txns = self.account_service.get_transaction_history(acc['account_id'])
                if txns:
                    has_transactions = True
                    response_parts.append(f"<br><strong>{acc['account_type']} account:</strong>")
                    for i, txn in enumerate(txns[:3]):  # Show only last 3 transactions per account
                        txn_type, amount, timestamp = txn
                        sign = "+" if txn_type in ["deposit", "transfer_in"] else "-"
                        response_parts.append(f"  {sign}ZMW {amount:.2f} ({txn_type}) on {timestamp[:10]}")
            
            if not has_transactions:
                return "No recent transactions found."
            
            return "<br>".join(response_parts)
        except Exception as e:
            print(f"Error in _get_transactions_response: {e}")
            return "I couldn't retrieve your transaction history. Please try again later."

    def _get_budget_summary_response(self):
        """Get budget summary"""
        try:
            budget_summary = self.purchase_service.get_budget_summary()
            if not budget_summary:
                return "You haven't set any budgets yet. Visit the 'Plans' section to create budgets."
            
            return (f"<strong>Budget summary:</strong><br>"
                   f"Total budget: ZMW {budget_summary['total_budget']:.2f}<br>"
                   f"Spent: ZMW {budget_summary['total_spent']:.2f}<br>"
                   f"Remaining: ZMW {budget_summary['remaining']:.2f}")
            
        except Exception as e:
            print(f"Error in _get_budget_summary_response: {e}")
            return "I couldn't retrieve your budget information. Please try again later."

    def _get_savings_goals_response(self):
        """Get savings goals"""
        try:
            goals = self.purchase_service.get_savings_goals()
            if not goals:
                return "You don't have any savings goals yet. Visit the 'Plans' section to create goals."
            
            response_parts = ["Your savings goals:"]
            for goal in goals:
                goal_name, target_amount, saved_amount = goal
                progress = (saved_amount / target_amount * 100) if target_amount > 0 else 0
                response_parts.append(f"• {goal_name}: ZMW {saved_amount:.2f}/ZMW {target_amount:.2f} ({progress:.1f}%)")
            
            return "<br>".join(response_parts)
            
        except Exception as e:
            print(f"Error in _get_savings_goals_response: {e}")
            return "I couldn't retrieve your savings goals. Please try again later."

    def _get_loans_response(self):
        """Get loan information"""
        try:
            loans = self.loan_service.get_loans_by_user(self.user_id)
            if not loans:
                return "You don't have any active loans. You can apply for one in the Loan section."
        
            response_parts = ["Here are your loans:"]
            for loan in loans:
                response_parts.append(
                    f"• {loan['loan_type']} of ZMW {loan['principal']:.2f}, "
                    f"remaining: ZMW {loan['balance']:.2f}, "
                    f"interest: {loan['interest_rate']}%, "
                    f"term: {loan['term']} months"
                )
            return "<br>".join(response_parts)
        except Exception as e:
            print(f"Error in _get_loans_response: {e}")
            return "I couldn't retrieve your loan information. Please try again later."

    def _get_expenses_response(self):
        """Get expenses response"""
        return "I can help you track expenses in the 'Plans' section. For now, I can help you with your account balances, transactions, budgets, and savings goals."

    def _get_complaint_response(self):
        """Handle user complaints"""
        return (
            "I'm sorry you're experiencing an issue 🙁. "
            "Could you describe the problem in more detail? "
            "I can log it for review, or if it's urgent please contact customer support or visit your nearest branch."
        )

    def _get_help_response(self):
        """Get help message"""
        return """<strong>I can help you with:</strong><br><br>
💰 <strong>Account Information</strong><br>
- "What's my balance?"<br>
- "Show my accounts"<br>
- "Recent transactions"<br><br>
📊 <strong>Budget & Planning</strong><br>
- "My budgets"<br>
- "Budget summary"<br><br>
🎯 <strong>Savings Goals</strong><br>
- "My savings goals"<br>
- "Savings progress"<br><br>
🏦 <strong>Loans</strong><br>
- "My loans"<br>
- "Loan details"<br><br>
⚠️ <strong>Issues</strong><br>
- "I have a problem"<br>
- "I want to make a complaint"<br><br>
Just ask me anything about your finances!"""