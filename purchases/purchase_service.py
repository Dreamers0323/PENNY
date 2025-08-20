# purchases/purchase_service.py
# this module deals with purchases and budgeting functionalities
from purchases.budget_planner import BudgetPlanner
from purchases.savings import SavingsGoals
from datetime import datetime

class PurchaseService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.budget_planner = BudgetPlanner()
        self.savings = SavingsGoals(user_id)

    # === Budget methods ===
    def set_overall_budget(self, amount, month=None, year=None):
        return self.budget_planner.set_overall_budget(self.user_id, amount, month, year)

    def set_budget_category(self, category, amount, month=None, year=None):
        return self.budget_planner.set_budget(self.user_id, category, amount, month, year)

    def get_budgets(self, month=None, year=None):
        return self.budget_planner.get_budgets(self.user_id, month, year)

    def get_budget_summary(self, month=None, year=None):
        return self.budget_planner.get_budget_summary(self.user_id, month, year)

    def delete_budget_category(self, category, month=None, year=None):
        return self.budget_planner.delete_budget_category(self.user_id, category, month, year)

    # === Savings methods ===
    def add_savings_goal(self, goal_name, target_amount):
        return self.savings.add_goal(goal_name, target_amount)

    def update_savings_progress(self, goal_name, amount):
        return self.savings.update_saved_amount(goal_name, amount)

    def get_savings_goals(self):
        return self.savings.get_goals()

    def delete_savings_goal(self, goal_name):
        return self.savings.delete_goal(goal_name)
