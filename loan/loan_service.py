# loan/loan_service.py
# handles the business logic for loan applications, repayments, and loan management.
# It provides methods to apply for loans, approve or reject them, and manage repayments.
from .models import Loan, LoanType, LoanStatus
from .loan_manager import apply_loan, get_loans_by_user, approve_loan_db, reject_loan_db, make_repayment_db, find_loan_db
from datetime import datetime

class LoanService:
    def __init__(self):
        pass  # Tables are managed by loan_manager now

    def apply_for_loan(self, user_id: str, principal: float, interest_rate: float,
                      term_months: int, loan_type: str, reason: str = "") -> Loan:
        """Create and store a new loan application"""
        loan_id = apply_loan(user_id, principal, interest_rate, term_months, loan_type, reason)
        monthly_payment = self._calculate_monthly_payment(principal, interest_rate, term_months)
        return Loan(
            id=loan_id,
            user_id=user_id,
            principal=principal,
            interest_rate=interest_rate,
            term_months=term_months,
            loan_type=loan_type,
            reason=reason,
            status=LoanStatus.PENDING.value,
            application_date=datetime.now().strftime('%Y-%m-%d'),
            monthly_payment=monthly_payment,
            total_repayment=0.0,
            balance_remaining=principal
        )

    def get_loans_by_user(self, user_id: str) -> list[Loan]:
        """Get all loans for a user"""
        loan_data = get_loans_by_user(user_id)
        return [
            Loan(
                id=loan['id'],
                user_id=loan['user_id'],
                principal=loan['principal'],
                interest_rate=loan['interest_rate'],
                term_months=loan['term_months'],
                loan_type=loan['loan_type'],
                reason=loan['reason'],
                status=loan['status'],
                application_date=loan['application_date'],
                monthly_payment=loan['monthly_payment'],
                total_repayment=loan['total_repayment'],
                balance_remaining=loan['balance_remaining']
            ) for loan in loan_data
        ]

    def approve_loan(self, loan_id: int) -> bool:
        """Approve a pending loan"""
        return approve_loan_db(loan_id)

    def reject_loan(self, loan_id: int) -> bool:
        """Reject a pending loan"""
        return reject_loan_db(loan_id)

    def make_repayment(self, loan_id: int, amount: float) -> bool:
        """Make a repayment on an approved loan"""
        return make_repayment_db(loan_id, amount)

    def _calculate_monthly_payment(self, principal: float, rate: float, term: int) -> float:
        """Calculate monthly payment using amortization formula"""
        monthly_rate = rate / 100 / 12
        if monthly_rate == 0:
            return principal / term
        return principal * monthly_rate * (1 + monthly_rate) ** term / ((1 + monthly_rate) ** term - 1)

    def find_loan(self, loan_id: int) -> Loan | None:
        """Find a loan by ID using the database"""
        loan = find_loan_db(loan_id)
        if loan:
            return Loan(**loan)
        return None