# 从新的 models.py 导入 User 模型和 db 实例
# 这样保持向后兼容，同时避免重复定义
from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 为了向后兼容，我们可以在这里添加一些额外的方法
# 但是主要的 User 模型定义在 models.py 中

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hashed password
    email = db.Column(db.String(100), nullable=False)  # 新增 email 属性
    score = db.Column(db.Integer, default=0)
    # 钱包相关字段
    wallet_address = db.Column(db.String(100), nullable=True)
    wallet_type = db.Column(db.String(20), default='metamask')
    bind_time = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, password, email):
        self.username = username
        self.password = generate_password_hash(password)  # store hashed password
        self.email = email  # 初始化 email 字段

    def check_password(self, password):
        """
        Check if the provided password matches the stored hashed password.
        """
        return check_password_hash(self.password, password)
    
    def bind_wallet(self, wallet_address, wallet_type='metamask'):
        """
        绑定钱包地址
        """
        self.wallet_address = wallet_address
        self.wallet_type = wallet_type
        self.bind_time = datetime.utcnow()
    
    def unbind_wallet(self):
        """
        解绑钱包
        """
        self.wallet_address = None
        self.wallet_type = 'metamask'
        self.bind_time = None
    
    def has_wallet_bound(self):
        """
        检查是否已绑定钱包
        """
        return self.wallet_address is not None
    
    def to_dict(self):
        """
        转换为字典格式，方便JSON序列化
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'score': self.score,
            'wallet_address': self.wallet_address,
            'wallet_type': self.wallet_type,
            'bind_time': self.bind_time.isoformat() if self.bind_time else None,
            'has_wallet_bound': self.has_wallet_bound()
        }

    def __repr__(self):
        return f'<User {self.username}>'

def create_user(username, password, email):
    """创建新用户的便捷函数"""
    user = User(
        username=username,
        email=email,
        password=generate_password_hash(password)
    )
    return user

def check_user_password(user, password):
    """检查用户密码的便捷函数"""
    return check_password_hash(user.password, password)

# 导出主要的类和函数，保持向后兼容
__all__ = ['User', 'db', 'create_user', 'check_user_password']
