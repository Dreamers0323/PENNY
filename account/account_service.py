# Account Service Module
# handle account creation, deposits, withdrawals, balance inquiries, transfers, and updates
# This module defines the AccountService class for managing accounts and transactions.
from account import SavingsAccount, CheckingAccount
from transactions import Transaction
from exceptions import AccountNotFoundError, InsufficientFundsError, InactiveAccountError
import uuid # For generating unique IDs
# This module provides the AccountService class for managing accounts and transactions.

class AccountService:
    def __init__(self):
        self.accounts = {}  # {account_id: Account}
        self.transactions = []  # List of Transaction

    def create_account(self, user_id: str, account_type: str):
        account_id = str(uuid.uuid4())
        if account_type == "Savings":
            account = SavingsAccount(account_id, user_id)
        elif account_type == "Checking":
            account = CheckingAccount(account_id, user_id)
        else:
            raise ValueError("Invalid account type.")
        self.accounts[account_id] = account
        return account

    def deposit(self, account_id: str, amount: float):
        account = self._get_active_account(account_id)
        account.deposit(amount)
        self._record_transaction(account_id, amount, "deposit")
        return account.balance

    def withdraw(self, account_id: str, amount: float):
        account = self._get_active_account(account_id)
        try:
            account.withdraw(amount)
        except ValueError as e:
            raise InsufficientFundsError(str(e))
        self._record_transaction(account_id, amount, "withdraw")
        return account.balance

    def transfer_funds(self, from_account_id: str, to_account_id: str, amount: float):
        from_account = self._get_active_account(from_account_id)
        to_account = self._get_active_account(to_account_id)

        if from_account.balance < amount:
            raise InsufficientFundsError("Insufficient funds for transfer.")

        from_account.withdraw(amount)
        to_account.deposit(amount)

        self._record_transaction(from_account_id, amount, "transfer_out")
        self._record_transaction(to_account_id, amount, "transfer_in")

        return from_account.balance, to_account.balance

    def check_funds(self, account_id: str):
        account = self._get_account(account_id)
        return account.check_funds()

    def update_account(self, account_id: str, **kwargs):
        account = self._get_account(account_id)
        account.update_account(**kwargs)
        return account

    def _get_account(self, account_id: str):
        if account_id not in self.accounts:
            raise AccountNotFoundError("Account not found.")
        return self.accounts[account_id]

    def _get_active_account(self, account_id: str):
        account = self._get_account(account_id)
        if not account.active:
            raise InactiveAccountError("Account is inactive.")
        return account

    def _record_transaction(self, account_id: str, amount: float, transaction_type: str):
        tx = Transaction(str(uuid.uuid4()), account_id, amount, transaction_type)
        self.transactions.append(tx)

    def get_transaction_history(self, account_id: str):
        return [tx for tx in self.transactions if tx.account_id == account_id]