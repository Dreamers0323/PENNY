# interfaces/authentication_service_interface.py
# this file defines an interface for authentication services.
# It uses the ABC module to create an abstract base class with an abstract method for logging in
from abc import ABC, abstractmethod

class IAuthenticationService(ABC):
    @abstractmethod
    def login(self, email: str, password: str) -> str:
        pass
