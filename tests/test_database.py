#!/usr/bin/env python3
"""
Test database setup and management for Quiz AI tests.
Creates and manages a separate test database to avoid interfering with production data.
"""

import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

load_dotenv()

# Test database configuration (aligned with backend env)
TEST_DB_HOST = os.getenv("MYSQL_HOST", "localhost")
TEST_DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
TEST_DB_USER = os.getenv("MYSQL_USER", "root")
TEST_DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "1234")
TEST_DB_NAME = os.getenv("MYSQL_TEST_DATABASE", "quiz_ai_test")  # Prefer separate test DB if permitted
DEFAULT_EXISTING_DB = os.getenv("MYSQL_DATABASE", "defaultdb")
# Allow disabling CREATE DATABASE on cloud plans (default: false)
ALLOW_CREATE_DB = os.getenv("MYSQL_ALLOW_CREATE_DB", "false").lower() in ("1", "true", "yes", "on")

# Resolve CA certificate path like backend
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> repo root (/QuizAI)
DEFAULT_TEST_CA_PATH = os.path.join(ROOT_DIR, "Backend", "ca.pem")
TEST_DB_SSL_CA = os.getenv("MYSQL_SSL_CA", DEFAULT_TEST_CA_PATH)

# Test run marker for safe cleanup in shared/production DB
TEST_RUN_ID = os.getenv("TEST_RUN_ID", "local")
TEST_EMAIL_PREFIX = f"quizai_test_{TEST_RUN_ID}_"
TEST_EMAIL_LIKE = TEST_EMAIL_PREFIX + "%"

class TestDatabaseManager:
    """Manages test database setup and cleanup."""
    
    def __init__(self):
        self.host = TEST_DB_HOST
        self.port = TEST_DB_PORT
        self.user = TEST_DB_USER
        self.password = TEST_DB_PASSWORD
        self.database = TEST_DB_NAME
        self.fallback_database = DEFAULT_EXISTING_DB
        self.table_prefix = ""
        self.created_db = False  # set to True if we successfully create the test DB
        self.allow_create_db = ALLOW_CREATE_DB
        # SSL kwargs (only if CA exists)
        self.ssl_kwargs = {}
        if TEST_DB_SSL_CA and os.path.exists(TEST_DB_SSL_CA):
            self.ssl_kwargs = {
                "ssl_ca": TEST_DB_SSL_CA,
                "ssl_verify_cert": True,
                "ssl_verify_identity": False,
            }

    def _base_connect_kwargs(self):
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            **self.ssl_kwargs,
        }

    def _connect(self, include_db=False):
        kwargs = self._base_connect_kwargs()
        if include_db:
            kwargs["database"] = self.database
        return mysql.connector.connect(**kwargs)
        
    def create_test_database(self):
        """Create the test database (if permitted) and tables.
        Falls back to using existing database with test_ table prefix if CREATE DATABASE is not allowed.
        """
        try:
            if self.allow_create_db:
                # Connect without DB to attempt DB creation
                cnx = mysql.connector.connect(**self._base_connect_kwargs())
                cursor = cnx.cursor()
                try:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                    self.created_db = True
                    print(f"✅ Test database '{self.database}' ensured/created.")
                except mysql.connector.Error as err:
                    # Handle lack of privilege to create databases (common on cloud services)
                    if getattr(err, "errno", None) in (errorcode.ER_DBACCESS_DENIED_ERROR, errorcode.ER_CANT_CREATE_DB) or "denied" in str(err).lower():
                        print(f"⚠️  CREATE DATABASE denied. Falling back to existing database '{self.fallback_database}'.")
                        self.database = self.fallback_database
                        self.table_prefix = "test_"
                        self.created_db = False
                    else:
                        raise
                finally:
                    cursor.close()
                    cnx.close()
            else:
                # Do not attempt DB creation; use existing production DB and mark test rows by email prefix
                self.database = self.fallback_database
                self.table_prefix = ""  # app uses real tables; we'll clean up by email prefix
                self.created_db = False
                print(f"ℹ️ Using existing database '{self.database}' for tests (no CREATE DATABASE). Test data marked by email prefix '{TEST_EMAIL_PREFIX}'.")

            # Connect to the chosen database and create tables
            cnx = self._connect(include_db=True)
            cursor = cnx.cursor()

            users_table = f"{self.table_prefix}users"
            quizzes_table = f"{self.table_prefix}quizzes"

            create_users_table = f"""
            CREATE TABLE IF NOT EXISTS {users_table} (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                mail VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
            """
            cursor.execute(create_users_table)

            create_quizzes_table = f"""
            CREATE TABLE IF NOT EXISTS {quizzes_table} (
                quiz_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                quiz_data JSON NOT NULL,
                mode VARCHAR(50) NOT NULL,
                duration INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES {users_table}(user_id) ON DELETE CASCADE
            );
            """
            cursor.execute(create_quizzes_table)

            cnx.commit()
            cursor.close()
            cnx.close()

            print(f"✅ Test database/tables prepared successfully (db_created={self.created_db}, using='{self.database}', prefix='{self.table_prefix}')")
            return True

        except mysql.connector.Error as err:
            print(f"❌ Error creating test database/tables: {err}")
            return False
    
    def clear_test_data(self):
        """Clear test data.
        - If we created a dedicated test DB: clear all rows in its tables.
        - If using production DB: only delete rows created in this run (by email prefix).
        """
        try:
            cnx = self._connect(include_db=True)
            cursor = cnx.cursor()

            if self.created_db:
                # Safe: dedicated test DB
                cursor.execute("DELETE FROM quizzes")
                cursor.execute("DELETE FROM users")
            else:
                # Shared/prod DB: only delete our run's data
                cursor.execute(
                    "DELETE FROM quizzes WHERE user_id IN (SELECT user_id FROM users WHERE mail LIKE %s)",
                    (TEST_EMAIL_LIKE,)
                )
                cursor.execute(
                    "DELETE FROM users WHERE mail LIKE %s",
                    (TEST_EMAIL_LIKE,)
                )
            
            cnx.commit()
            cursor.close()
            cnx.close()
            
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error clearing test data: {err}")
            return False
    
    def drop_test_database(self):
        """Drop the test database if we created it; otherwise remove test-run data only."""
        try:
            if self.created_db:
                # Connect without DB to drop it
                cnx = mysql.connector.connect(**self._base_connect_kwargs())
                cursor = cnx.cursor()
                cursor.execute(f"DROP DATABASE IF EXISTS {self.database}")
                cnx.commit()
                cursor.close()
                cnx.close()
                print(f"✅ Test database '{self.database}' dropped successfully")
            else:
                # Shared/prod DB: just delete rows created in this run
                self.clear_test_data()
                print(f"✅ Test data cleaned from '{self.database}' (email prefix '{TEST_EMAIL_PREFIX}')")
            return True
        
        except mysql.connector.Error as err:
            print(f"❌ Error cleaning up test database/tables: {err}")
            return False
    
    def get_connection(self):
        """Get a connection to the test database (with SSL/port)."""
        return self._connect(include_db=True)

# Global test database manager instance
test_db = TestDatabaseManager()

if __name__ == "__main__":
    # Setup test database when run directly
    test_db.create_test_database()
