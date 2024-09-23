import configparser

import cryptography.fernet
import mysql.connector
from mysql.connector import Error


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
                # Read configuration
                config = configparser.ConfigParser()
                config.read('config.ini')

                # Get database configuration
                db_config = config['mysql']
                # password decrypt
                cipher_suite = cryptography.fernet.Fernet(db_config['DB_KEY'].encode())
                encrypted_password = db_config['encrypted_password']
                decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
                self._connection = mysql.connector.connect(
                    host=db_config['host'],
                    port=int(db_config['port']),
                    database=db_config['database'],
                    user=db_config['user'],
                    password=decrypted_password
                )
                if self._connection.is_connected():
                    print("Connection to Google MySQL database is successful!")
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
    # Get the singleton instance of the database connection
    db_connection_instance = DatabaseConnection()
    connection = db_connection_instance.create_connection()

    if connection:
        # Perform some database operations
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print("Databases:")
        for database in databases:
            print(database)
        # close connection
        db_connection_instance.close_connection()


if __name__ == '__main__':
    main()
