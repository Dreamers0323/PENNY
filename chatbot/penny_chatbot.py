# chatbot/penny_chatbot.py
# Penny chatbot for user interactions (Accounts + Purchases)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from account.account_service import AccountService
from purchases.purchase_service import PurchaseService
from loan.loan_service import LoanService

class PennyChatbot:
    def __init__(self, user_id, session=None):
        self.user_id = user_id
        self.session = session  # Flask session object
        
        # Initialize state from session or create new
        if session and 'penny_state' in session:
            self.state = session['penny_state']
            self.context = session.get('penny_context', {})
        else:
            self.state = None
            self.context = {}
        
        try:
            self.account_service = AccountService()
            self.purchase_service = PurchaseService(user_id)
            self.loan_service = LoanService()
        except Exception as e:
            print(f"Error initializing PennyChatbot services: {e}")
            raise
    
    def _save_state(self):
        """Save state to session"""
        if self.session is not None:
            self.session['penny_state'] = self.state
            self.session['penny_context'] = self.context
    
    def _reset_state(self):
        """Reset conversation state"""
        self.state = None
        self.context = {}
        self._save_state()

    def process_message(self, user_input):
        try:
            user_input = user_input.lower().strip()
            print(f"Processing message: '{user_input}' for user {self.user_id}")
            print(f"Current state: {self.state}, Context: {self.context}")

            # === STATEFUL CONVERSATIONS (must come first) ===
            if self.state == "purchase_item":
                response = self._handle_purchase_flow(user_input)
                self._save_state()
                return response

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

            # === PURCHASE PLANNING (entry point) ===
            elif "buy" in user_input or "purchase" in user_input:
                self.state = "purchase_item"
                self.context = {}
                self._save_state()
                return "That's nice! What would you like to buy?"

            # === DEFAULT RESPONSE ===
            else:
                return "I'm not sure I understand. Try asking me about your balance, accounts, transactions, budgets, or savings goals. Type 'help' to see what I can do."

        except Exception as e:
            print(f"Error in process_message: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."

    def _handle_purchase_flow(self, user_input):
        """Handle the stateful purchase planning conversation"""
        try:
            print(f"In purchase flow - Context: {self.context}")
            
            # Step 1: Get the item name
            if "item" not in self.context:
                self.context["item"] = user_input
                return f"Okay, a {user_input} sounds great! How much does it cost and what's your monthly salary? Please tell me both amounts in ZMW."

            # Step 2: Get cost and salary
            if "cost" not in self.context or "salary" not in self.context:
                # Try to extract numbers from the input
                import re
                numbers = re.findall(r'\d+', user_input)
                numbers = [int(n) for n in numbers if n.isdigit()]
                
                if len(numbers) >= 2:
                    self.context["cost"] = numbers[0]  # First number is cost
                    self.context["salary"] = numbers[1]  # Second number is salary
                    return "Do you have family members? (yes/no)"
                elif len(numbers) == 1:
                    if "cost" not in self.context:
                        self.context["cost"] = numbers[0]
                        return f"Great! The {self.context['item']} costs ZMW {numbers[0]:,}. Now, what's your monthly salary?"
                    else:
                        self.context["salary"] = numbers[0]
                        return "Do you have family members? (yes/no)"
                else:
                    return "Please tell me the price in ZMW. For example, just say '5000' or 'it costs 5000'."

            # Step 3: Ask about family
            if "has_family" not in self.context:
                if any(word in user_input.lower() for word in ["yes", "yeah", "yep", "i do", "i have"]):
                    self.context["has_family"] = True
                    return "How many family members do you have (including yourself)?"
                elif any(word in user_input.lower() for word in ["no", "nope", "none", "don't", "dont"]):
                    self.context["has_family"] = False
                    self.context["family_size"] = 1  # Just the user
                    return self._calculate_purchase_plan()
                else:
                    return "Please answer yes or no - do you have family members?"

            # Step 4: Get family size if they have family
            if self.context.get("has_family") and "family_size" not in self.context:
                try:
                    family_size = int(user_input.strip())
                    if family_size < 1:
                        return "Please enter a valid number of family members (1 or more)."
                    self.context["family_size"] = family_size
                    return self._calculate_purchase_plan()
                except ValueError:
                    return "Please enter the number of family members as a number (e.g., 4)."

            # Fallback - calculate the plan
            return self._calculate_purchase_plan()
            
        except Exception as e:
            print(f"Error in _handle_purchase_flow: {e}")
            self._reset_state()
            return "Sorry, I encountered an error. Let's start over - what would you like to buy?"

    def _calculate_purchase_plan(self):
        """Calculate and return the purchase plan"""
        try:
            cost = self.context["cost"]
            salary = self.context["salary"]
            family_size = self.context.get("family_size", 1)
            item = self.context.get("item", "item")
            
            # Calculate living costs based on Zambian data
            if family_size == 1:
                living_cost = 3000  # Base cost for single person
            else:
                # For families, use the ZMW 11,000 for family of 6 as baseline
                living_cost = (11000 / 6) * family_size
            
            # Calculate disposable income
            disposable_income = salary - living_cost
            
            if disposable_income <= 0:
                self._reset_state()
                return (f"⚠️ I'm sorry, but based on your salary of ZMW {salary:,} and "
                       f"estimated living costs of ZMW {living_cost:,.0f} for {family_size} people, "
                       f"you don't have enough disposable income to save for this purchase right now. "
                       f"You might want to consider increasing your income or reducing expenses first.")
            
            # Calculate how much they can save (assuming 70% of disposable income for safety)
            monthly_savings = disposable_income * 0.7
            months_to_save = cost / monthly_savings
            
            # Create response with range
            min_months = max(1, int(months_to_save - 2))
            max_months = int(months_to_save + 2)
            avg_months = int(months_to_save)
            
            response = (f"✅ <strong>Purchase Plan Complete!</strong><br><br>"
                       f"📊 <strong>Your Financial Breakdown:</strong><br>"
                       f"• Monthly Salary: ZMW {salary:,}<br>"
                       f"• Living Costs: ZMW {living_cost:,.0f}<br>"
                       f"• Available for Savings: ZMW {disposable_income:,.0f}<br>"
                       f"• Recommended Monthly Savings: ZMW {monthly_savings:,.0f}<br><br>"
                       f"🎯 <strong>Your {item} Goal:</strong><br>"
                       f"• Target Cost: ZMW {cost:,}<br>"
                       f"• Estimated Time: <strong>{avg_months} months</strong><br>"
                       f"• Range: {min_months}-{max_months} months<br><br>"
                       f"💡 <strong>Tip:</strong> Set up an automatic transfer of ZMW {monthly_savings:,.0f} "
                       f"each month to reach your goal faster!")
            
            # Reset conversation state
            self._reset_state()
            return response
                
        except Exception as e:
            print(f"Error in _calculate_purchase_plan: {e}")
            self._reset_state()
            return "Sorry, I encountered an error calculating your plan. Please try again."

    # ... (keep all your existing methods like _get_balance_response, etc.)
    
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
                # Access dictionary keys instead of unpacking as tuple
                goal_name = goal['goal_name']
                target_amount = float(goal['target_amount'])  # Convert to float
                saved_amount = float(goal['saved_amount'])    # Convert to float
                
                progress = (saved_amount / target_amount * 100) if target_amount > 0 else 0
                remaining = target_amount - saved_amount
                
                if remaining <= 0:
                    status = "✅ Complete!"
                else:
                    status = f"ZMW {remaining:.2f} remaining"
                
                response_parts.append(
                    f"• {goal_name}: ZMW {saved_amount:.2f}/ZMW {target_amount:.2f} "
                    f"({progress:.1f}%) - {status}"
                )
            
            return "<br>".join(response_parts)
            
        except Exception as e:
            print(f"Error in _get_savings_goals_response: {e}")
            import traceback
            traceback.print_exc()
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
🛒 <strong>Purchase Planning</strong><br>
- "I want to buy something"<br>
- "Help me plan a purchase"<br><br>
🏦 <strong>Loans</strong><br>
- "My loans"<br>
- "Loan details"<br><br>
⚠️ <strong>Issues</strong><br>
- "I have a problem"<br>
- "I want to make a complaint"<br><br>
Just ask me anything about your finances!"""