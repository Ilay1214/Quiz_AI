import mysql.connector
import os
import ssl
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Database configuration
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))  # Default MySQL port
DB_USER = os.getenv("MYSQL_USER", "root")  # Allow custom user
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")  # More generic name
DB_NAME = os.getenv("MYSQL_DATABASE", "users")  # Allow custom DB name

# SSL configuration for cloud databases (e.g., Aiven)
# in Backend/Database/database_setup.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> Backend/
DEFAULT_CA_PATH = os.path.join(BASE_DIR, "ca.pem")
DB_SSL_CA = os.getenv("MYSQL_SSL_CA", DEFAULT_CA_PATH)
# Track if database is available
db_available = False

def get_db_config():
    config = {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'autocommit': False,
        'connection_timeout': 10
    }

    # Prefer full DSN if provided
    dsn = os.getenv('MYSQL_URL') or os.getenv('DATABASE_URL')
    host_val = dsn if dsn else config.get('host')

    if host_val:
        host_str = str(host_val).strip().strip('"').strip("'")
        if '://' in host_str:
            parsed = urlparse(host_str)
            if parsed.hostname:
                config['host'] = parsed.hostname
            if parsed.port:
                config['port'] = parsed.port
            if parsed.username and not config.get('user'):
                config['user'] = parsed.username
            if parsed.password and not config.get('password'):
                config['password'] = parsed.password
            if parsed.path and len(parsed.path) > 1:
                # do not override DB_NAME env if already set
                config.setdefault('database', parsed.path.lstrip('/'))
        else:
            if ':' in host_str and not isinstance(config.get('port'), int):
                try:
                    h, p = host_str.rsplit(':', 1)
                    config['host'] = h
                    config['port'] = int(p)
                except Exception:
                    config['host'] = host_str
            else:
                config['host'] = host_str

    if DB_SSL_CA and os.path.exists(DB_SSL_CA):
        config['ssl_ca'] = DB_SSL_CA
        config['ssl_verify_cert'] = True
        config['ssl_verify_identity'] = False

    return config

def setup_database():
    """Setup database and tables. Returns True if successful, False otherwise."""
    global db_available
    
    # Check if required configuration is present
    if not DB_HOST or not DB_PASSWORD:
        print("WARNING: Database configuration incomplete (MYSQL_HOST or MYSQL_PASSWORD missing)")
        print("The application will run without database functionality.")
        db_available = False
        return False
    
    try:
        print(f"Attempting to connect to MySQL at {DB_HOST}:{DB_PORT}...")
        
        # Connect to MySQL server without specifying a database
        config = get_db_config()
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' checked/created successfully.")

        cursor.close()
        cnx.close()

        # Reconnect to the newly created/existing database
        config = get_db_config()
        config['database'] = DB_NAME
        cnx = mysql.connector.connect(**config)
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
        
        print(f"Database setup completed successfully!")
        db_available = True
        return True

    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        print(f"Error Code: {err.errno if hasattr(err, 'errno') else 'N/A'}")
        print(f"SQLSTATE: {err.sqlstate if hasattr(err, 'sqlstate') else 'N/A'}")
        print("\nThe application will continue running with limited functionality.")
        print("Database-dependent features will return appropriate error messages.")
        db_available = False
        return False
    except Exception as e:
        print(f"Unexpected error during database setup: {e}")
        print("The application will continue running with limited functionality.")
        db_available = False
        return False

if __name__ == "__main__":
    setup_database()
