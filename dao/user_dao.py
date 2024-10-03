from app import db  # 保持不变，因为 `db` 在 `app.py` 中已全局定义
from model.user import User


class UserDAO:
    def __init__(self):
        pass

    def add_user(self, username, password, email):
        """
        Register a new user with a hashed password.
        """
        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    def get_user_by_username(self, username):
        """
        Retrieve a user by their username.
        """
        return User.query.filter_by(username=username).first()

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def update_user_score(self, username, score):
        """
        Update the score for a specific user.
        """
        user = self.get_user_by_username(username)
        if user:
            user.score += score
            db.session.commit()

    def get_leaderboard(self):
        """
        Retrieve the leaderboard based on users' scores.
        """
        return User.query.order_by(User.score.desc()).all()
