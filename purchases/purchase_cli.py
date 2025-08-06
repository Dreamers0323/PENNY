# purchase_cli.py

from .budget_planner import BudgetPlanner
from .savings import SavingsGoals # <-- NEW import

def launch_purchase_cli(user_id):
    planner = BudgetPlanner()
    savings = SavingsGoals(user_id)  # <-- NEW object

    while True:
        print("\n=== 📋 PURCHASE & BUDGET MENU ===")
        print("1. Set overall monthly budget")
        print("2. Add a category budget")
        print("3. View my budgets")
        print("4. Update a category budget")
        print("5. View budget summary")
        print("6. Delete a category")
        print("7. Manage savings goals")  # <-- NEW MENU OPTION
        print("8. Exit to main menu")

        choice = input("Choose an option: ")

        if choice == "1":
            total = float(input("💸 Enter your total budget for the month (e.g., 10000): "))
            month = input("📆 Month [press Enter for current]: ") or None
            year = input("📆 Year [press Enter for current]: ") or None
            planner.set_overall_budget(user_id, total, month, int(year) if year else None)

        elif choice == "2":
            category = input("🏷️ Enter category (e.g., food, rent): ")
            amount = float(input("Enter amount (K): "))
            month = input("📆 Month [press Enter for current]: ") or None
            year = input("📆 Year [press Enter for current]: ") or None
            planner.set_budget(user_id, category, amount, month, int(year) if year else None)

        elif choice == "3":
            month = input("📆 Month to view [press Enter for current]: ") or None
            year = input("📆 Year to view [press Enter for current]: ") or None
            planner.get_budgets(user_id, month, int(year) if year else None)

        elif choice == "4":
            category = input("🏷️ Category to update: ")
            new_amount = float(input("💰 New amount (K): "))
            month = input("📆 Month [press Enter for current]: ") or None
            year = input("📆 Year [press Enter for current]: ") or None
            planner.update_budget(user_id, category, new_amount, month, int(year) if year else None)

        elif choice == "5":
            month = input("📆 Month for summary [press Enter for current]: ") or None
            year = input("📆 Year for summary [press Enter for current]: ") or None
            planner.get_budget_summary(user_id, month, int(year) if year else None)

        elif choice == "6":
            category = input("🏷️ Enter category to delete: ")
            month = input("📆 Month [press Enter for current]: ") or None
            year = input("📆 Year [press Enter for current]: ") or None
            planner.delete_budget_category(user_id, category, month, int(year) if year else None)

        elif choice == "7":
            while True:
                print("\n=== 💰 SAVINGS GOALS MENU ===")
                print("1. Set savings goal")
                print("2. View savings goals")
                print("3. Add money to savings goal")  # <-- NEW OPTION
                print("4. Delete savings goal")
                print("5. Back to main menu")

                savings_choice = input("Choose an option: ")

                if savings_choice == "1":
                    goal_name = input("🏁 Goal name (e.g., Vacation): ")
                    amount = float(input("💵 Goal amount: "))
                    # CHANGE 1: Use add_goal instead of set_savings_goal (removed deadline since it's not in your database)
                    savings.add_goal(goal_name, amount)
                    print(f"✅ Savings goal '{goal_name}' created with target of K{amount}")

                elif savings_choice == "2":
                    # CHANGE 2: Use get_goals and display the results properly
                    goals = savings.get_goals()
                    if goals:
                        print("\n💰 Your Savings Goals:")
                        print("-" * 50)
                        for goal_name, target_amount, saved_amount in goals:
                            progress_percent = (saved_amount / target_amount * 100) if target_amount > 0 else 0
                            print(f"🎯 Goal: {goal_name}")
                            print(f"💰 Target: K{target_amount:,.2f}")
                            print(f"💵 Saved: K{saved_amount:,.2f}")
                            print(f"📊 Progress: {progress_percent:.1f}%")
                            print(f"💸 Remaining: K{(target_amount - saved_amount):,.2f}")
                            print("-" * 30)
                    else:
                        print("📭 No savings goals found. Create one first!")

                elif savings_choice == "3":
                    # NEW OPTION: Add money to existing goal
                    goal_name = input("🏁 Enter goal name to add money to: ")
                    amount = float(input("💵 Amount to add: "))
                    savings.update_saved_amount(goal_name, amount)
                    print(f"✅ Added K{amount} to '{goal_name}' savings goal")

                elif savings_choice == "4":
                    goal_name = input("❌ Enter goal name to delete: ")
                    # CHANGE 3: Use delete_goal instead of delete_savings_goal (no user_id needed since it's in constructor)
                    savings.delete_goal(goal_name)
                    print(f"❌ Deleted savings goal '{goal_name}'")

                elif savings_choice == "5":
                    break
                else:
                    print("⚠️ Invalid savings option. Try again.")

        elif choice == "8":
            print("👋 Returning to Main Menu...")
            break
        else:
            print("⚠️ Invalid option. Try again.")

    planner.close()