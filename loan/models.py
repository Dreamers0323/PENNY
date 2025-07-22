# loan/models.py
# This file contains the models for the loan application system.
# loan, repayment, and enums for loan types and statuses.
# define the Loan types and Repayment models, along with enums for loan types and statuses as loan data structure.
# It includes classes for Loan and Repayment, as well as enums for LoanType and Loan
from enum import Enum # for defining enumerations
from datetime import date

class LoanType(Enum):
    FULL = "Full"
    INSTALLMENT = "Installment"
    COLLATERAL = "Collateral"

class LoanStatus(Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REPAID = "Repaid"

class Loan:
    def __init__(self, loan_id, user_id, principal, interest_rate, term_months, loan_type: LoanType, reason: str):
        self.loan_id = loan_id
        self.user_id = user_id
        self.principal = principal
        self.interest_rate = interest_rate
        self.term_months = term_months
        self.loan_type = loan_type
        self.reason = reason
        self.start_date = date.today()
        self.status = LoanStatus.PENDING
        self.repayments = []
    
    def calculate_total_amount(self):
        return self.principal * (1 + self.interest_rate / 100)

    def calculate_monthly_payment(self):
        return self.calculate_total_amount() / self.term_months

    def add_repayment(self, repayment):
        self.repayments.append(repayment)

    def get_balance_remaining(self):
        paid = sum([r.amount for r in self.repayments])
        return self.calculate_total_amount() - paid

class Repayment:
    def __init__(self, amount, payment_date=None):
        self.amount = amount
        self.payment_date = payment_date or date.today()
