#!/usr/bin/env python3
"""
Test database setup and management for Quiz AI tests.
Creates and manages a separate test database to avoid interfering with production data.
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Test database configuration
TEST_DB_HOST = os.getenv("MYSQL_HOST", "localhost")
TEST_DB_USER = os.getenv("MYSQL_USER", "root")
TEST_DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "1234")
TEST_DB_NAME = "quiz_ai_test"  # Separate test database

class TestDatabaseManager:
    """Manages test database setup and cleanup."""
    
    def __init__(self):
        self.host = TEST_DB_HOST
        self.user = TEST_DB_USER
        self.password = TEST_DB_PASSWORD
        self.database = TEST_DB_NAME
        
    def create_test_database(self):
        """Create the test database and tables."""
        try:
            # Connect without specifying database to create it
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = cnx.cursor()
            
            # Create test database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.close()
            cnx.close()
            
            # Connect to test database and create tables
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            cursor = cnx.cursor()
            
            # Create users table
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                mail VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
            """
            cursor.execute(create_users_table)
            
            # Create quizzes table
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
            
            cnx.commit()
            cursor.close()
            cnx.close()
            
            print(f"✅ Test database '{self.database}' created successfully")
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error creating test database: {err}")
            return False
    
    def clear_test_data(self):
        """Clear all data from test database tables."""
        try:
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            cursor = cnx.cursor()
            
            # Clear tables in correct order (due to foreign key constraints)
            cursor.execute("DELETE FROM quizzes")
            cursor.execute("DELETE FROM users")
            
            cnx.commit()
            cursor.close()
            cnx.close()
            
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error clearing test data: {err}")
            return False
    
    def drop_test_database(self):
        """Drop the entire test database."""
        try:
            cnx = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = cnx.cursor()
            
            cursor.execute(f"DROP DATABASE IF EXISTS {self.database}")
            
            cnx.commit()
            cursor.close()
            cnx.close()
            
            print(f"✅ Test database '{self.database}' dropped successfully")
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error dropping test database: {err}")
            return False
    
    def get_connection(self):
        """Get a connection to the test database."""
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

# Global test database manager instance
test_db = TestDatabaseManager()

if __name__ == "__main__":
    # Setup test database when run directly
    test_db.create_test_database()
