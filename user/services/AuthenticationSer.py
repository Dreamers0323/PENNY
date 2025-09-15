# services/authentication_service.py
from ..interfaces.AuthenticationServiceInter import IAuthenticationService
from ..interfaces.userRepoInterface import IUserRepository

class AuthenticationService(IAuthenticationService):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> int:
        """Login with email - original method"""
        user = self.user_repository.get_user_by_email(email)
        
        if not user:
            raise ValueError("User not found.")
        
        if user.password != password:
            raise ValueError("Invalid password.")
        
        if not user.is_verified:
            print("Login successful, but user is not verified yet.")
        
        return user.id

    def login_with_username(self, username: str, password: str) -> int:
        """Login with username - new method"""
        user = self.user_repository.find_by_username(username)
        
        if not user:
            raise ValueError("User not found.")
        
        if user.password != password:
            raise ValueError("Invalid password.")
        
        if not user.is_verified:
            print("Login successful, but user is not verified yet.")
        
        return user.id