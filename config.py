import os

from cryptography.fernet import Fernet
import logging


class Config:
    # MySQL Database Configuration
    MYSQL_HOST = 'rm-uf6wz9309g448ly67no.mysql.rds.aliyuncs.com'
    MYSQL_PORT = 3306
    MYSQL_DATABASE = 'ai-game'
    MYSQL_USER = 'chenghao'
    MYSQL_ENCRYPTED_PASSWORD = 'gAAAAABm7lDveEoiAYFwXOrNnGcrLGPAAzVur5KBmg2bj_EoFczIrjZEoBBJFWVs3wYXV-ihZJ-b1-19St_-9IWbdPal9_SfZg=='
    MYSQL_DB_KEY = 'L3tLdmglGKFdIeYe9xHLPa_ebkN3TX-NVZGK79ExoQk='

    @staticmethod
    def decrypt_password(encrypted_password, key):
        """Decrypt the encrypted password using Fernet."""
        cipher_suite = Fernet(key.encode())
        decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
        return decrypted_password

    # Decrypt the password
    decrypted_password = decrypt_password.__func__(MYSQL_ENCRYPTED_PASSWORD, MYSQL_DB_KEY)

    # SQLAlchemy Configuration for MySQL
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{decrypted_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)  # A random secret key for Flask security features

    LOG_LEVEL = logging.DEBUG  # 日志级别可以是 DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
