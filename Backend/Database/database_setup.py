import mysql.connector
import os
import ssl
from dotenv import load_dotenv
from urllib.parse import urlparse
from mysql.connector import errorcode, pooling

load_dotenv()

# Database configuration
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))  # Default MySQL port
DB_USER = os.getenv("MYSQL_USER", "root")  # Allow custom user
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")  # More generic name
DB_NAME = os.getenv("MYSQL_DATABASE", "users")  # Allow custom DB name

# Debug: Print what env vars are loaded
print(f"[DEBUG] Environment variables loaded:")
print(f"  MYSQL_HOST: {DB_HOST}")
print(f"  MYSQL_PORT: {DB_PORT}")
print(f"  MYSQL_USER: {DB_USER}")
print(f"  MYSQL_DATABASE: {DB_NAME}")
print(f"  DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"  MYSQL_URL: {os.getenv('MYSQL_URL')}")

# SSL configuration for cloud databases (e.g., Aiven)
# in Backend/Database/database_setup.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> Backend/
DEFAULT_CA_PATH = os.path.join(BASE_DIR, "ca.pem")
DB_SSL_CA = os.getenv("MYSQL_SSL_CA", DEFAULT_CA_PATH)
# Track if database is available
db_available = False
# Connection pool (initialized lazily)
db_pool = None

def _resolve_ssl_ca_path(path_val: str | None) -> str | None:
    """Resolve SSL CA path. Accepts a direct file or a directory containing a .pem file.
    Returns a file path or None if not found.
    """
    if not path_val:
        return None
    try:
        p = path_val.strip().strip('"').strip("'")
        if not p:
            return None
        if os.path.isdir(p):
            # Try common filenames first
            candidates = [
                os.path.join(p, "ca.pem"),
                os.path.join(p, "server-ca.pem"),
                os.path.join(p, "ca.crt"),
            ]
            for c in candidates:
                if os.path.isfile(c):
                    return c
            # Fallback: first .pem file in directory
            for name in os.listdir(p):
                if name.lower().endswith(".pem"):
                    candidate = os.path.join(p, name)
                    if os.path.isfile(candidate):
                        return candidate
            return None
        if os.path.isfile(p):
            return p
    except Exception:
        pass
    return None

def get_db_config():
    config = {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'autocommit': False,
        'connection_timeout': 10
    }

    # Prefer full DSN if provided (MYSQL_URL or DATABASE_URL)
    dsn = os.getenv('MYSQL_URL') or os.getenv('DATABASE_URL')
    host_val = dsn if dsn else config.get('host')
    
    print(f"[DEBUG] get_db_config - DSN found: {dsn}")
    print(f"[DEBUG] get_db_config - host_val: {host_val}")

    if host_val:
        host_str = str(host_val).strip().strip('"').strip("'")
        if '://' in host_str:
            parsed = urlparse(host_str)
            if parsed.hostname:
                config['host'] = parsed.hostname
            if parsed.port:
                config['port'] = parsed.port
            # When DSN given, let it override user/password/database
            if parsed.username:
                config['user'] = parsed.username
            if parsed.password:
                config['password'] = parsed.password
            if parsed.path and len(parsed.path) > 1:
                config['database'] = parsed.path.lstrip('/')
        else:
            # Always support host:port literal (avoid using a literal like 'localhost:25066' as hostname)
            if ':' in host_str and not host_str.startswith('['):  # naive IPv6 guard
                try:
                    h, p = host_str.rsplit(':', 1)
                    config['host'] = h
                    if p.isdigit():
                        config['port'] = int(p)
                except Exception:
                    config['host'] = host_str
            else:
                config['host'] = host_str

    # SSL handling
    resolved_ca = _resolve_ssl_ca_path(DB_SSL_CA)
    if resolved_ca and os.path.exists(resolved_ca):
        config['ssl_ca'] = resolved_ca
        config['ssl_verify_cert'] = True
        config['ssl_verify_identity'] = False
    
    print(f"[DEBUG] Final config: host={config.get('host')}, port={config.get('port')}, "
          f"user={config.get('user')}, database={config.get('database')}, "
          f"ssl_ca={config.get('ssl_ca')}")

    return config

def setup_database():
    """Setup database and tables. Returns True if successful, False otherwise.
    Tries to connect directly to DB_NAME first. If the database is missing, it will
    attempt to create it. If CREATE DATABASE is not permitted (managed DB), it will
    continue if connecting to the target database succeeds.
    """
    global db_available

    # Check if required configuration is present
    if not DB_HOST or not DB_PASSWORD:
        print("WARNING: Database configuration incomplete (MYSQL_HOST or MYSQL_PASSWORD missing)")
        print("The application will run without database functionality.")
        db_available = False
        return False

    try:
        base_config = get_db_config()
        config_with_db = dict(base_config)
        config_with_db['database'] = DB_NAME

        def _connect(cfg):
            return mysql.connector.connect(**cfg)

        try:
            # Attempt direct connection to the target database
            cnx = _connect(config_with_db)
        except mysql.connector.Error as err:
            if getattr(err, 'errno', None) == errorcode.ER_BAD_DB_ERROR:
                # Database does not exist. Try to create it (may fail on managed DBs)
                print(f"Database '{DB_NAME}' not found. Attempting to create it...")
                try:
                    server_cnx = _connect(base_config)
                    cursor = server_cnx.cursor()
                    try:
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
                        print(f"Database '{DB_NAME}' checked/created successfully.")
                    finally:
                        cursor.close()
                        server_cnx.close()
                except mysql.connector.Error as create_err:
                    print(f"NOTICE: Could not create database '{DB_NAME}' (likely lack of privilege): {create_err}")
                    # Continue – DB might already exist on managed services
                # Retry connecting to the target database
                cnx = _connect(config_with_db)
            else:
                # Different error – rethrow
                raise

        cursor = cnx.cursor()

        # Create users table if it doesn't exist
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            mail VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );
        """
        cursor.execute(create_users_table)
        print("Table 'users' checked/created successfully.")

        # Create quizzes table if it doesn't exist
        create_quizzes_table = """
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
        cursor.execute(create_quizzes_table)
        print("Table 'quizzes' checked/created successfully.")

        cnx.commit()
        cursor.close()
        cnx.close()

        print("Database setup completed successfully!")
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

def get_pooled_connection(database: str | None = None):
    """Return a pooled MySQL connection. Initializes the pool lazily."""
    global db_pool
    cfg = get_db_config()
    cfg['database'] = database or DB_NAME
    if db_pool is None:
        size = int(os.getenv("MYSQL_POOL_SIZE", "5"))
        db_pool = pooling.MySQLConnectionPool(
            pool_name="quiz_ai_pool",
            pool_size=size,
            **cfg,
        )
    return db_pool.get_connection()

if __name__ == "__main__":
    setup_database()
