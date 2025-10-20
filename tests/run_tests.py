#!/usr/bin/env python3
"""
Quiz AI Test Runner - Orchestrates database verification and test execution.
This script NEVER creates databases or tables. It verifies that the existing
schema is present and uses test-scoped data that is cleaned up after the run.
"""

import subprocess
import sys
import os
import requests
import time
from test_database import test_db


def check_server_running():
    """Check if the Flask server is running."""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def setup_test_environment():
    """Set up the test environment without any DDL operations."""
    print("🔧 Setting up test environment...")
    
    # Step 1: Verify existing database and schema (no creation)
    print("📋 Step 1: Verifying existing database and schema...")
    if test_db.verify_existing_database():
        print("✅ Database and schema verified")
    else:
        print("⚠️  Database verification failed or DB disconnected — proceeding in demo mode")
    
    # Step 2: Clear any existing test data
    print("📋 Step 2: Clearing prior test data...")
    if test_db.clear_test_data():
        print("✅ Prior test data cleared (or skipped if DB unavailable)")
    else:
        print("⚠️  Skipped clearing test data (DB unavailable)")
    
    return True


def cleanup_test_environment():
    """Clean up test data only (no schema or DB changes)."""
    print("\n🧹 Cleaning up test environment...")
    if test_db.drop_test_database():
        print("✅ Test data cleaned up successfully (or skipped if DB unavailable)")
    else:
        print("⚠️  Skipped cleaning test data (DB unavailable)")


def run_all_tests():
    """Run all tests using the consolidated test file."""
    print("🚀 Running all tests...")
    print("-" * 50)
    
    try:
        # Import and run the consolidated test suite
        from all_tests import QuizAITester
        
        tester = QuizAITester()
        success = tester.run_all_tests()
        
        return success
        
    except ImportError as e:
        print(f"❌ Error importing test suite: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main test runner function."""
    print("=" * 70)
    print("QUIZ AI TEST RUNNER")
    print("=" * 70)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Flask server is not running on localhost:8000")
        print("\nPlease start the server first:")
        print("1. Open a new terminal")
        print("2. cd Backend")
        print("3. python3 app.py")
        print("\nThen run this script again.")
        return False
    
    print("✅ Flask server is running")
    
    try:
        # Step 1: Setup test environment (verify + clear)
        if not setup_test_environment():
            return False
        
        # Step 2: Run all tests
        success = run_all_tests()
        
        # Step 3: Cleanup (always run)
        cleanup_test_environment()
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        cleanup_test_environment()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        cleanup_test_environment()
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("Quiz AI Test Runner")
        print("==================")
        print("This script runs the complete Quiz AI test suite.")
        print("\nUsage:")
        print("  python3 run_tests.py")
        print("\nBefore running:")
        print("  1. Start the Flask server: cd Backend && python3 app.py")
        print("  2. Install test dependencies: pip install -r tests_requirements.txt")
        print("  3. Run this script")
        sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1)
