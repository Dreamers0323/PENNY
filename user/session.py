# user/session.py (you may create a 'utils' folder if not existing)
# This module provides a simple session management system to store the current user's ID.
# It allows setting and getting the current user ID, which can be used for tracking user sessions

class Session:
    current_user_id = None

    @classmethod
    def set(cls, key, value):
        if key == "current_user_id":
            cls.current_user_id = value

    @classmethod
    def get(cls, key):
        if key == "current_user_id":
            return cls.current_user_id
