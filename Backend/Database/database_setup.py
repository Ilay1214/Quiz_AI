import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Provider-agnostic database configuration
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE", "users")

# SSL Configuration for cloud providers (optional)
DB_SSL_CA = os.getenv("MYSQL_SSL_CA")  # Path to CA certificate
DB_SSL_REQUIRED = os.getenv("MYSQL_SSL_REQUIRED", "false").lower() == "true"

def get_connection_config():
    """Get database connection configuration with optional SSL support"""
    config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "autocommit": False,
        "raise_on_warnings": True
    }
    
    # Add SSL configuration if required
    if DB_SSL_REQUIRED and DB_SSL_CA:
        config["ssl_ca"] = DB_SSL_CA
        config["ssl_verify_cert"] = True
        config["ssl_verify_identity"] = True
    elif DB_SSL_REQUIRED:
        # Use SSL without certificate verification (less secure)
        config["ssl_disabled"] = False
    
    return config

def setup_database():
    try:
        # Connect to MySQL server without specifying a database
        cnx = mysql.connector.connect(**get_connection_config())
        cursor = cnx.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' checked/created successfully.")

        cursor.close()
        cnx.close()

        # Reconnect to the newly created/existing database
        cnx = mysql.connector.connect(
            **get_connection_config(),
            database=DB_NAME
        )
        cursor = cnx.cursor()

        # Create users table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            mail VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );
        """
        cursor.execute(create_table_query)
        print("Table 'users' checked/created successfully.")

        # Create quizzes table if it doesn't exist
        create_quizzes_table_query = """
        CREATE TABLE IF NOT EXISTS quizzes (
            quiz_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            quiz_data JSON NOT NULL,
            mode VARCHAR(50) NOT NULL,
            duration INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_quizzes_table_query)
        print("Table 'quizzes' checked/created successfully.")

        cnx.commit()
        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        # In a real application, you might want to log this error and exit
        # or raise it to prevent the application from starting.

if __name__ == "__main__":
    setup_database()
