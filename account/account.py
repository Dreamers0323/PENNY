# this file defines the base Account class and its derived classes
# and implements basic account operations like deposit and withdraw
from abc import ABC, abstractmethod # Abstract Base Class for Accounts

class Account(ABC): # This class represents a generic bank account
    def __init__(self, account_id: str, user_id: str, balance: float = 0.0):
        self.account_id = account_id
        self.user_id = user_id
        self.balance = balance
        self.active = True
    
    @abstractmethod
    def account_type(self):
        pass

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        return self.balance

    def check_funds(self):
        return self.balance

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True

    def update_account(self, **kwargs):
        # Example: update account type or other properties
        for key, value in kwargs.items():
            setattr(self, key, value)

class SavingsAccount(Account):
    def account_type(self):
        return "Savings"

class CheckingAccount(Account):
    def account_type(self):
        return "Checking"