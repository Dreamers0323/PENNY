# user.py
# this code defines a User class with attributes and default values. represents both employees and customers.
# It uses the dataclass decorator to automatically generate special methods like __init__ and __repr
# this module is used to create user objects with attributes like id, username, email, password, role, and verification status.
from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    email: str
    password: str
    role: str  # 'employee' or 'customer'
    is_verified: bool = False
