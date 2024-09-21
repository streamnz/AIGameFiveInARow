from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hashed password
    score = db.Column(db.Integer, default=0)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)  # store hashed password

    def check_password(self, password):
        """
        Check if the provided password matches the stored hashed password.
        """
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'
