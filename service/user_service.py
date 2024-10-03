from dao.user_dao import UserDAO
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:
    def __init__(self):
        self.user_dao = UserDAO()

    def register_user(self, username, password, email):
        """
        Register a new user.
        """
        existing_user = self.user_dao.get_user_by_email(email)
        if existing_user:
            return {"status": "error", "message": "Email already exists."}

        user = self.user_dao.add_user(username, password, email)
        return {"status": "success", "message": "User registered successfully.", "user": user}

    def login_user(self, username, password):
        """
        Handle user login.
        """
        user = self.user_dao.get_user_by_email(username)
        if not user or not check_password_hash(user.password, password):
            return {"status": "error", "message": "Invalid username or password."}

        return {"status": "success", "user": user}

    def get_leaderboard(self):
        """
        Get the leaderboard.
        """
        leaderboard = self.user_dao.get_leaderboard()
        return [{"username": user.username, "score": user.score} for user in leaderboard]
