# test_budget.py

from budget_planner import BudgetPlanner

def main():
    planner = BudgetPlanner()

    user_id = input("👤 Enter your user ID: ")

    while True:
        print("\n=== 📋 BUDGET MENU ===")
        print("1. Set overall monthly budget")
        print("2. Add a category budget")
        print("3. View my budgets")
        print("4. Update a category budget")
        print("5. View budget summary")
        print("6. Delete a category")
        print("7. Exit")

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
            year = input("📆 Year [press Enter for current]: ") or None
            planner.get_budget_summary(user_id, month, int(year) if year else None)

        elif choice == "6":
            category = input("🏷️ Enter category to delete: ")
            month = input("📆 Month [press Enter for current]: ") or None
            year = input("📆 Year [press Enter for current]: ") or None
            planner.delete_budget_category(user_id, category, month, int(year) if year else None)


        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid option. Try again.")

    planner.close()

if __name__ == "__main__":
    main()
