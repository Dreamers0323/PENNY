import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from account.account_service import AccountService, InsufficientFundsError

class PennyGUI:
    def __init__(self, root, account_service, user_id):
        self.root = root
        self.root.title("Penny Banking Bot")
        self.root.geometry("400x400")
        
        self.account_service = account_service
        self.user_id = user_id  # logged-in user (replace later with real login)
        
        self.main_menu()

    def clear_screen(self):
        """Helper to clear the window before switching menus"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="📱 Penny Main Menu", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Button(self.root, text="Account", width=20, command=self.account_menu).pack(pady=5)
        tk.Button(self.root, text="Loan", width=20, state="disabled").pack(pady=5)   # later
        tk.Button(self.root, text="Purchases", width=20, state="disabled").pack(pady=5) # later
        tk.Button(self.root, text="Chat with Penny", width=20, command=self.chatbot_window).pack(pady=5)
        tk.Button(self.root, text="Logout", width=20, command=self.root.quit).pack(pady=20)

    def account_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="🏦 Penny Account Module", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self.root, text="Deposit", width=20, command=self.deposit_window).pack(pady=5)
        tk.Button(self.root, text="Withdraw", width=20, command=self.withdraw_window).pack(pady=5)
        tk.Button(self.root, text="Check Balance", width=20, command=self.show_balances).pack(pady=5)
        tk.Button(self.root, text="Back to Main Menu", width=20, command=self.main_menu).pack(pady=20)

    def chatbot_window(self):
        messagebox.showinfo("Chatbot", "🤖 Penny: Hi! Ask me about balances, loans, or savings.")

    def deposit_window(self):
        self.clear_screen()
        tk.Label(self.root, text="💰 Deposit Money", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Account ID").pack()
        account_id_entry = tk.Entry(self.root)
        account_id_entry.pack()

        tk.Label(self.root, text="Amount").pack()
        amount_entry = tk.Entry(self.root)
        amount_entry.pack()

        def do_deposit():
            try:
                acc_id = account_id_entry.get()
                amount = float(amount_entry.get())
                new_balance = self.account_service.deposit(self.user_id, acc_id, amount)
                messagebox.showinfo("Success", f"✅ Deposit successful.\nNew balance: {new_balance}")
                self.account_menu()
            except Exception as e:
                messagebox.showerror("Error", f"❌ {str(e)}")

        tk.Button(self.root, text="Deposit", command=do_deposit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.account_menu).pack()

    def withdraw_window(self):
        self.clear_screen()
        tk.Label(self.root, text="💸 Withdraw Money", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Account ID").pack()
        account_id_entry = tk.Entry(self.root)
        account_id_entry.pack()

        tk.Label(self.root, text="Amount").pack()
        amount_entry = tk.Entry(self.root)
        amount_entry.pack()

        def do_withdraw():
            try:
                acc_id = account_id_entry.get()
                amount = float(amount_entry.get())
                new_balance = self.account_service.withdraw(self.user_id, acc_id, amount)
                messagebox.showinfo("Success", f"✅ Withdrawal successful.\nNew balance: {new_balance}")
                self.account_menu()
            except InsufficientFundsError:
                messagebox.showerror("Error", "❌ Insufficient funds.")
            except Exception as e:
                messagebox.showerror("Error", f"❌ {str(e)}")

        tk.Button(self.root, text="Withdraw", command=do_withdraw).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.account_menu).pack()

    def show_balances(self):
        accounts = self.account_service.get_accounts_by_user(self.user_id)
        balances = "\n".join([f"{a['account_type']} (ID: {a['account_id']}) → Balance: {a['balance']} ZMW" for a in accounts])
        messagebox.showinfo("Your Accounts", balances if balances else "No accounts found.")

if __name__ == "__main__":
    root = tk.Tk()
    service = AccountService()   # use your real db-backed service
    user_id = "user123"          # mock user for now
    app = PennyGUI(root, service, user_id)
    root.mainloop()
