# services/authentication_service.py
# This module provides authentication services for user login.

from ..interfaces.AuthenticationServiceInter import IAuthenticationService
from ..interfaces.userRepoInterface import IUserRepository

class AuthenticationService(IAuthenticationService):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> int:  # 🔁 Changed return type to int (user ID)
        user = self.user_repository.get_user_by_email(email)

        if not user:
            raise ValueError("User not found.")

        if user.password != password:
            raise ValueError("Invalid password.")

        if not user.is_verified:
            print("Login successful, but user is not verified yet.")  # ✅ Print warning but continue
            return user.id  # Still return the ID so user can access limited features if needed

        return user.id  # ✅ Return the user ID for session storage
