import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet
import base64

# 加载 .env 文件
load_dotenv()

def generate_key():
    """生成新的加密密钥"""
    return Fernet.generate_key().decode()

def encrypt_password(password, key):
    """加密数据库密码"""
    cipher_suite = Fernet(key.encode())
    encrypted_password = cipher_suite.encrypt(password.encode()).decode()
    return encrypted_password

def decrypt_password(encrypted_password, key):
    """解密数据库密码"""
    cipher_suite = Fernet(key.encode())
    decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
    return decrypted_password

def verify_database_connection(host, port, database, user, password):
    """验证数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        if connection.is_connected():
            print("数据库连接成功！")
            connection.close()
            return True
    except Error as e:
        print(f"数据库连接失败: {e}")
        return False

class DatabaseConnection:
    _instance = None

    def __init__(self):
        self._connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def create_connection(self):
        """Create a database connection to the MySQL database."""
        if self._connection is None or not self._connection.is_connected():
            try:
                # 从环境变量获取配置
                host = os.getenv('MYSQL_HOST')
                port = int(os.getenv('MYSQL_PORT', 3306))
                database = os.getenv('MYSQL_DATABASE')
                user = os.getenv('MYSQL_USER')
                encrypted_password = os.getenv('MYSQL_ENCRYPTED_PASSWORD')
                db_key = os.getenv('MYSQL_DB_KEY')

                # 解密密码
                decrypted_password = decrypt_password(encrypted_password, db_key)

                self._connection = mysql.connector.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=decrypted_password
                )
                if self._connection.is_connected():
                    print("Connection to MySQL database is successful!")
                    print("System is ready...")
                    print("Try Admin User: user_name=admin,password=admin")
            except Error as e:
                print(f"Error: '{e}'")
                self._connection = None
        return self._connection

    def close_connection(self):
        """Close the database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            print("MySQL connection is closed")
            self._connection = None


def main():
    print("\n=== 当前 .env 配置信息 ===")
    host = os.getenv('MYSQL_HOST')
    port = int(os.getenv('MYSQL_PORT', 3306))
    database = os.getenv('MYSQL_DATABASE')
    user = os.getenv('MYSQL_USER')
    encrypted_password = os.getenv('MYSQL_ENCRYPTED_PASSWORD')
    db_key = os.getenv('MYSQL_DB_KEY')

    print(f"数据库主机: {host}")
    print(f"数据库端口: {port}")
    print(f"数据库名称: {database}")
    print(f"数据库用户: {user}")
    print(f"加密密钥: {db_key}")
    print(f"加密密码: {encrypted_password}")

    # 验证当前配置
    print("\n=== 验证当前配置 ===")
    try:
        if db_key and encrypted_password:
            decrypted_password = decrypt_password(encrypted_password, db_key)
            if verify_database_connection(host, port, database, user, decrypted_password):
                print("当前配置验证成功！")
            else:
                print("当前配置验证失败！")
        else:
            print("当前配置不完整，需要生成新配置")
    except Exception as e:
        print(f"验证过程出错: {e}")

    # 生成新的配置
    print("\n=== 生成新的配置 ===")
    choice = input("是否需要生成新的配置？(y/n): ")
    if choice.lower() == 'y':
        # 生成新密钥
        new_key = generate_key()
        print(f"\n新的密钥: {new_key}")
        
        # 使用新密钥加密新密码
        new_password = input("\n请输入新的数据库密码: ")
        new_encrypted_password = encrypt_password(new_password, new_key)
        print(f"加密后的密码: {new_encrypted_password}")
        
        print("\n=== 新的配置信息 ===")
        print("请将以下内容更新到 .env 文件中：")
        print(f"MYSQL_DB_KEY={new_key}")
        print(f"MYSQL_ENCRYPTED_PASSWORD={new_encrypted_password}")
        
        # 验证新配置
        print("\n=== 验证新配置 ===")
        if verify_database_connection(host, port, database, user, new_password):
            print("新配置验证成功！")
        else:
            print("新配置验证失败！")


if __name__ == '__main__':
    main()
