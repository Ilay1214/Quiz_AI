#!/usr/bin/env python3
"""
Test database setup and management for Quiz AI tests.
Uses the same database as the backend application (no separate test database).
"""

import mysql.connector
import os
import sys

# Add Backend to path to import database_setup
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Backend'))

# Import the EXACT same database configuration from the backend
from Database.database_setup import (
    DB_HOST,
    DB_PORT, 
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    get_db_config
)

# Test run marker for safe cleanup - only delete test-created data
TEST_RUN_ID = os.getenv("TEST_RUN_ID", "local")
TEST_EMAIL_PREFIX = f"test_{TEST_RUN_ID}_"
TEST_EMAIL_LIKE = TEST_EMAIL_PREFIX + "%"

class TestDatabaseManager:
    """Manages test database setup and cleanup."""
    
    def __init__(self):
        # Use exact same database as the backend
        self.host = DB_HOST
        self.port = DB_PORT
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME  # Same database the app uses
        print(f"Test database manager using: {self.database} at {self.host}:{self.port}")

    def get_connection(self):
        """Get a connection to the database using backend's config."""
        config = get_db_config()
        config['database'] = self.database
        return mysql.connector.connect(**config)
        
    def create_test_database(self):
        """Verify database connection and tables exist.
        Does NOT create a new database - uses the existing production database.
        Tables should already exist from the backend's setup_database().
        """
        try:
            print(f"ℹ️  Using existing database '{self.database}' for tests.")
            print(f"ℹ️  Test users will have email prefix: '{TEST_EMAIL_PREFIX}'")
            
            # Just verify we can connect and tables exist
            cnx = self.get_connection()
            cursor = cnx.cursor()
            
            # Verify tables exist
            cursor.execute("SHOW TABLES LIKE 'users'")
            if not cursor.fetchone():
                print("❌ 'users' table not found. Run backend setup first.")
                return False
                
            cursor.execute("SHOW TABLES LIKE 'quizzes'")
            if not cursor.fetchone():
                print("❌ 'quizzes' table not found. Run backend setup first.")
                return False
            
            cursor.close()
            cnx.close()
            
            print(f"✅ Database connection verified. Using '{self.database}' with existing tables.")
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error connecting to database: {err}")
            return False
    
    def clear_test_data(self):
        """Clear only test-created data from production database.
        Deletes only users with test email prefix and their associated quizzes.
        """
        try:
            cnx = self.get_connection()
            cursor = cnx.cursor()
            
            # Delete quizzes for test users first (foreign key constraint)
            cursor.execute(
                "DELETE FROM quizzes WHERE user_id IN (SELECT user_id FROM users WHERE mail LIKE %s)",
                (TEST_EMAIL_LIKE,)
            )
            deleted_quizzes = cursor.rowcount
            
            # Then delete test users
            cursor.execute(
                "DELETE FROM users WHERE mail LIKE %s",
                (TEST_EMAIL_LIKE,)
            )
            deleted_users = cursor.rowcount
            
            cnx.commit()
            cursor.close()
            cnx.close()
            
            print(f"✅ Cleared {deleted_users} test users and {deleted_quizzes} test quizzes")
            return True
            
        except mysql.connector.Error as err:
            print(f"❌ Error clearing test data: {err}")
            return False
    
    def drop_test_database(self):
        """Clean up test data from the production database.
        Never drops the database itself - only removes test-created data.
        """
        # Just clean up test data, never drop the actual database
        return self.clear_test_data()

# Global test database manager instance
test_db = TestDatabaseManager()

if __name__ == "__main__":
    # Setup test database when run directly
    test_db.create_test_database()
