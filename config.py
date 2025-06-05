import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import logging
import sys

# 加载 .env 文件
load_dotenv()

def validate_env_vars():
    """验证必要的环境变量是否存在"""
    required_vars = [
        'MYSQL_HOST',
        'MYSQL_PORT',
        'MYSQL_DATABASE',
        'MYSQL_USER',
        'MYSQL_ENCRYPTED_PASSWORD',
        'MYSQL_DB_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"错误: 以下环境变量未设置: {', '.join(missing_vars)}")
        print("请确保 .env 文件包含所有必要的配置项")
        sys.exit(1)

class Config:
    # 验证环境变量
    validate_env_vars()

    # MySQL Database Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_ENCRYPTED_PASSWORD = os.getenv('MYSQL_ENCRYPTED_PASSWORD')
    MYSQL_DB_KEY = os.getenv('MYSQL_DB_KEY')

    @staticmethod
    def decrypt_password(encrypted_password, key):
        """Decrypt the encrypted password using Fernet."""
        try:
            cipher_suite = Fernet(key.encode())
            decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
            return decrypted_password
        except Exception as e:
            print(f"解密密码时出错: {str(e)}")
            print("请确保 MYSQL_DB_KEY 和 MYSQL_ENCRYPTED_PASSWORD 格式正确")
            sys.exit(1)

    # Decrypt the password
    try:
        decrypted_password = decrypt_password.__func__(MYSQL_ENCRYPTED_PASSWORD, MYSQL_DB_KEY)
    except Exception as e:
        print(f"初始化配置时出错: {str(e)}")
        sys.exit(1)

    # SQLAlchemy Configuration for MySQL
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{decrypted_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Logging Configuration
    LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'DEBUG'))
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
