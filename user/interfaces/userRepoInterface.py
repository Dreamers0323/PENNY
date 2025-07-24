# interfaces/user_repository_interface.py
# this code defines an interface for user repository operations.
# It uses the ABC module to create an abstract base class with abstract methods for adding and retrieving users.
# this module is used to define the contract for user repository implementations.
from abc import ABC, abstractmethod
from ..Penny_user import User

class IUserRepository(ABC):

    @abstractmethod # This is an abstract base class for user repository operations
    # It defines the methods that any user repository implementation must provide.
    def add_user(self, user: User):
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User:
        pass
