# services/registration_service.py
from Penny_user import User
from interfaces.userRepoInterface import IUserRepository

class RegistrationService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def register(self, username, email, password, role):
        if self.user_repository.get_user_by_email(email):
            raise ValueError("Email already exists.")

        if len(password) < 5:
            raise ValueError("Password must be at least 5 characters long.")

        if role == "employee" and not username.startswith("ENTK"):
            raise ValueError("Employee usernames must start with 'ENTK'.")

        user = User(id=0, username=username, email=email, password=password, role=role)
        self.user_repository.add_user(user)
        return "Registration successful"
