# for custom exceptions related to account operations which is cleaner and more maintainable for error handling.
class AccountNotFoundError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

class InactiveAccountError(Exception):
    pass
