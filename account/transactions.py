# This module defines the Transaction class for handling financial transactions.
# from __future__ import annotations
from datetime import datetime

class Transaction:
    def __init__(self, transaction_id: str, account_id: str, amount: float, transaction_type: str):
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.amount = amount
        self.transaction_type = transaction_type  # deposit, withdraw, transfer
        self.timestamp = datetime.now()