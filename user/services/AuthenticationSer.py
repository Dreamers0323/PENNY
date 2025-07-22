# services/authentication_service.py
from interfaces.AuthenticationServiceInter import IAuthenticationService
from interfaces.userRepoInterface import IUserRepository

class AuthenticationService(IAuthenticationService):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def login(self, email: str, password: str) -> str:
        user = self.user_repository.get_user_by_email(email)

        if not user:
            raise ValueError("User not found.")

        if user.password != password:
            raise ValueError("Invalid password.")

        if not user.is_verified:
            return "Login successful, but user is not verified yet."

        return f"Login successful. Welcome {user.username}!"
