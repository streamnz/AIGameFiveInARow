from dao.user_dao import UserDAO
from model.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError


class UserService:
    def __init__(self):
        self.user_dao = UserDAO()

    def get_user_by_email(self, email):
        """
        Get user by email address.
        """
        return self.user_dao.get_user_by_email(email)

    def register_user(self, username, password, email):
        """
        Register a new user.
        """
        if self.user_dao.get_user_by_username(username):
            return {"status": "error", "message": "Username already exists."}
        if self.user_dao.get_user_by_email(email):
            return {"status": "error", "message": "Email already exists."}
        try:
            user = self.user_dao.add_user(username, password, email)
            return {"status": "success", "message": "User registered successfully.", "user": user}
        except IntegrityError:
            return {"status": "error", "message": "Username or email already exists."}

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

    def bind_wallet(self, user_id, wallet_address, wallet_type='metamask'):
        """
        绑定用户钱包
        """
        # 验证钱包地址格式（简单的以太坊地址验证）
        if not self._is_valid_ethereum_address(wallet_address):
            return {"status": "error", "message": "Invalid wallet address format."}
        
        # 检查钱包地址是否已被其他用户绑定
        existing_user = self.user_dao.get_user_by_wallet_address(wallet_address)
        if existing_user and existing_user.id != user_id:
            return {"status": "error", "message": "This wallet address is already bound to another account."}
        
        # 绑定钱包
        user = self.user_dao.bind_user_wallet(user_id, wallet_address, wallet_type)
        if user:
            return {
                "status": "success", 
                "message": "Wallet bound successfully.",
                "user": user.to_dict()
            }
        else:
            return {"status": "error", "message": "User not found."}
    
    def unbind_wallet(self, user_id):
        """
        解绑用户钱包
        """
        user = self.user_dao.unbind_user_wallet(user_id)
        if user:
            return {
                "status": "success", 
                "message": "Wallet unbound successfully.",
                "user": user.to_dict()
            }
        else:
            return {"status": "error", "message": "User not found."}
    
    def get_user_wallet_info(self, user_id):
        """
        获取用户钱包信息
        """
        user = User.query.filter_by(id=user_id).first()
        
        if user:
            return {
                "status": "success",
                "wallet_info": {
                    "has_wallet_bound": user.has_wallet_bound(),
                    "wallet_address": user.wallet_address,
                    "wallet_type": user.wallet_type,
                    "bind_time": user.bind_time.isoformat() if user.bind_time else None
                }
            }
        else:
            return {"status": "error", "message": "User not found."}
    
    def _is_valid_ethereum_address(self, address):
        """
        简单的以太坊地址格式验证
        """
        import re
        # 以太坊地址格式：0x开头，后跟40个十六进制字符
        pattern = r'^0x[a-fA-F0-9]{40}$'
        return bool(re.match(pattern, address))
