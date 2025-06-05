from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建数据库实例
db = SQLAlchemy()

class GameRecord(db.Model):
    """游戏记录模型"""
    __tablename__ = 'game_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    winner = db.Column(db.String(20), nullable=False)  # 'black', 'white', 'draw'
    moves_count = db.Column(db.Integer, nullable=False)
    game_duration = db.Column(db.Integer)  # 游戏时长（秒）
    ai_type = db.Column(db.String(50), default='deepseek')  # AI 类型
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 建立与用户的关系（User 模型在 model/user.py 中定义）
    # user = db.relationship('User', backref=db.backref('game_records', lazy=True))

    def __repr__(self):
        return f'<GameRecord {self.id}: {self.winner}>'

    def to_dict(self):
        """将游戏记录转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'winner': self.winner,
            'moves_count': self.moves_count,
            'game_duration': self.game_duration,
            'ai_type': self.ai_type,
            'created_at': self.created_at.isoformat()
        } 