# loan/loan_service.py
# handles the business logic for loan applications, repayments, and loan management.
# It provides methods to apply for loans, approve or reject them, and manage repayments.
from models import Loan, LoanType, LoanStatus, Repayment

class LoanService:
    def __init__(self):
        self.loans = []  # In-memory storage for now

    def apply_for_loan(self, loan_id, user_id, principal, interest_rate, term, loan_type, reason):
        loan = Loan(loan_id, user_id, principal, interest_rate, term, loan_type, reason)
        self.loans.append(loan)
        return loan

    def get_loans_by_user(self, user_id):
        return [loan for loan in self.loans if loan.user_id == user_id]

    def approve_loan(self, loan_id):
        loan = self._find_loan(loan_id)
        if loan:
            loan.status = LoanStatus.APPROVED
        return loan

    def reject_loan(self, loan_id):
        loan = self._find_loan(loan_id)
        if loan:
            loan.status = LoanStatus.REJECTED
        return loan

    def make_repayment(self, loan_id, amount):
        loan = self._find_loan(loan_id)
        if loan and loan.status == LoanStatus.APPROVED:
            repayment = Repayment(amount)
            loan.add_repayment(repayment)

            if loan.get_balance_remaining() <= 0:
                loan.status = LoanStatus.REPAID
            return repayment
        return None

    def _find_loan(self, loan_id):
        for loan in self.loans:
            if loan.loan_id == loan_id:
                return loan
        return None
