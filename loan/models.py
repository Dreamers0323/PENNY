# loan/models.py
# This file contains the models for the loan application system.
# loan, repayment, and enums for loan types and statuses.
# define the Loan types and Repayment models, along with enums for loan types and statuses as loan data structure.
# It includes classes for Loan and Repayment, as well as enums for LoanType and Loan

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class LoanType(Enum):
    FULL = "Full"
    INSTALLMENT = "Installment"
    COLLATERAL = "Collateral"

class LoanStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

@dataclass
class Loan:
    id: Optional[int] = None
    user_id: str = ""
    principal: float = 0.0
    interest_rate: float = 0.0
    term_months: int = 0
    loan_type: str = ""
    reason: str = ""
    status: str = "pending"
    application_date: Optional[str] = None
    approval_date: Optional[str] = None
    monthly_payment: float = 0.0
    total_repayment: float = 0.0
    balance_remaining: float = 0.0

@dataclass
class Repayment:
    id: Optional[int] = None
    loan_id: int = 0
    amount: float = 0.0
    payment_date: str = ""
    created_at: Optional[str] = None