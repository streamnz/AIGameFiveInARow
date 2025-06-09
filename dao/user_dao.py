from models import db  # 修复循环引用，只导入db实例
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

    def bind_user_wallet(self, user_id, wallet_address, wallet_type='metamask'):
        """
        绑定用户钱包
        """
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.bind_wallet(wallet_address, wallet_type)
            db.session.commit()
            return user
        return None

    def unbind_user_wallet(self, user_id):
        """
        解绑用户钱包
        """
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.unbind_wallet()
            db.session.commit()
            return user
        return None

    def get_user_by_wallet_address(self, wallet_address):
        """
        根据钱包地址查找用户
        """
        return User.query.filter_by(wallet_address=wallet_address).first()

    def update_user_wallet(self, user_id, wallet_address, wallet_type='metamask'):
        """
        更新用户钱包信息
        """
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.bind_wallet(wallet_address, wallet_type)
            db.session.commit()
            return user
        return None
