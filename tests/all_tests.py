#!/usr/bin/env python3
"""
Consolidated test suite for Quiz AI API.
Tests health endpoint and authentication functionality using isolated test database.
"""

import requests
import json
import time
import io
import os
from faker import Faker
from test_database import test_db, TEST_EMAIL_PREFIX

fake = Faker()

class QuizAITester:
    """Main test class for Quiz AI API."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.health_endpoint = f"{base_url}/api/health"
        self.register_endpoint = f"{base_url}/api/register"
        self.login_endpoint = f"{base_url}/api/login"
        self.generate_questions_endpoint = f"{base_url}/api/generate-questions"
        self.job_status_endpoint = f"{base_url}/api/job-status"
        
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    def log(self, message, status="INFO"):
        """Log a message with status."""
        symbols = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️", "SECTION": "📋"}
        print(f"{symbols.get(status, 'ℹ️')} {message}")
    
    def record_result(self, test_name, passed, message=""):
        """Record test result."""
        if passed:
            self.passed += 1
            self.log(f"{test_name}: {message}", "PASS")
        else:
            self.failed += 1
            self.log(f"{test_name}: {message}", "FAIL")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
    
    # Health Tests
    def test_health_endpoint_exists(self):
        """Test that the health endpoint exists and returns 200."""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            if response.status_code == 200:
                self.record_result("Health Endpoint Exists", True, "Returns 200 OK")
                return True
            else:
                self.record_result("Health Endpoint Exists", False, f"Returned {response.status_code}")
                return False
        except Exception as e:
            self.record_result("Health Endpoint Exists", False, f"Connection error: {e}")
            return False
    
    def test_health_response_format(self):
        """Test that the health endpoint returns proper JSON."""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            data = response.json()
            
            if isinstance(data, dict) and data.get('status') == 'ok':
                self.record_result("Health Response Format", True, "Valid JSON with status: ok")
                return True
            else:
                self.record_result("Health Response Format", False, f"Invalid format: {data}")
                return False
        except Exception as e:
            self.record_result("Health Response Format", False, f"Error: {e}")
            return False
    
    def test_health_response_time(self):
        """Test that the health endpoint responds quickly."""
        try:
            start_time = time.time()
            response = requests.get(self.health_endpoint, timeout=5)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200 and response_time < 1.0:
                self.record_result("Health Response Time", True, f"{response_time:.3f}s")
                return True
            else:
                self.record_result("Health Response Time", False, f"{response_time:.3f}s (too slow)")
                return False
        except Exception as e:
            self.record_result("Health Response Time", False, f"Error: {e}")
            return False
    
    # Authentication Tests
    def test_user_registration_success(self):
        """Test successful user registration."""
        test_email = TEST_EMAIL_PREFIX + fake.email()
        test_password = fake.password(length=12)
        
        payload = {
            "mail": test_email,
            "password": test_password
        }
        
        try:
            response = requests.post(
                self.register_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get('message') == "User registered successfully":
                    self.record_result("User Registration Success", True, "User created successfully")
                    return True
                else:
                    self.record_result("User Registration Success", False, f"Wrong message: {data}")
                    return False
            else:
                self.record_result("User Registration Success", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.record_result("User Registration Success", False, f"Error: {e}")
            return False
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        test_email = TEST_EMAIL_PREFIX + fake.email()
        test_password = fake.password(length=12)
        
        payload = {
            "mail": test_email,
            "password": test_password
        }
        
        try:
            # First registration
            response1 = requests.post(
                self.register_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Second registration with same email
            response2 = requests.post(
                self.register_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response1.status_code == 201 and response2.status_code == 409:
                self.record_result("Duplicate Email Rejection", True, "Correctly rejected duplicate")
                return True
            else:
                self.record_result("Duplicate Email Rejection", False, 
                                 f"Status codes: {response1.status_code}, {response2.status_code}")
                return False
        except Exception as e:
            self.record_result("Duplicate Email Rejection", False, f"Error: {e}")
            return False
    
    def test_user_registration_missing_fields(self):
        """Test registration with missing fields."""
        test_cases = [
            {},  # Empty payload
            {"mail": TEST_EMAIL_PREFIX + fake.email()},  # Missing password
            {"password": fake.password(length=12)},  # Missing email
        ]
        
        all_passed = True
        for i, payload in enumerate(test_cases):
            try:
                response = requests.post(
                    self.register_endpoint,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code != 400:
                    all_passed = False
                    break
            except Exception:
                all_passed = False
                break
        
        if all_passed:
            self.record_result("Registration Missing Fields", True, "All invalid payloads rejected")
            return True
        else:
            self.record_result("Registration Missing Fields", False, "Some invalid payloads accepted")
            return False
    
    def test_user_login_success(self):
        """Test successful user login."""
        test_email = TEST_EMAIL_PREFIX + fake.email()
        test_password = fake.password(length=12)
        
        # Register user first
        register_payload = {
            "mail": test_email,
            "password": test_password
        }
        
        try:
            # Register
            register_response = requests.post(
                self.register_endpoint,
                json=register_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if register_response.status_code != 201:
                self.record_result("User Login Success", False, "Registration failed")
                return False
            
            # Login
            login_response = requests.post(
                self.login_endpoint,
                json=register_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code == 200:
                data = login_response.json()
                required_fields = ['message', 'user_id', 'mail']
                
                if all(field in data for field in required_fields):
                    self.record_result("User Login Success", True, f"Login successful for {test_email}")
                    return True
                else:
                    self.record_result("User Login Success", False, "Missing required fields in response")
                    return False
            else:
                self.record_result("User Login Success", False, f"Status {login_response.status_code}")
                return False
        except Exception as e:
            self.record_result("User Login Success", False, f"Error: {e}")
            return False
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        test_email = TEST_EMAIL_PREFIX + fake.email()
        test_password = fake.password(length=12)
        
        # Register user first
        register_payload = {
            "mail": test_email,
            "password": test_password
        }
        
        try:
            # Register
            requests.post(
                self.register_endpoint,
                json=register_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Try login with wrong password
            wrong_login = {
                "mail": test_email,
                "password": "wrong_password"
            }
            
            response = requests.post(
                self.login_endpoint,
                json=wrong_login,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 401:
                self.record_result("Invalid Credentials Rejection", True, "Correctly rejected invalid login")
                return True
            else:
                self.record_result("Invalid Credentials Rejection", False, f"Status {response.status_code}")
                return False
        except Exception as e:
            self.record_result("Invalid Credentials Rejection", False, f"Error: {e}")
            return False
    
    def test_complete_auth_flow(self):
        """Test complete authentication flow."""
        test_email = TEST_EMAIL_PREFIX + fake.email()
        test_password = fake.password(length=15)
        
        try:
            # Step 1: Register
            register_payload = {
                "mail": test_email,
                "password": test_password
            }
            
            register_response = requests.post(
                self.register_endpoint,
                json=register_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if register_response.status_code != 201:
                self.record_result("Complete Auth Flow", False, "Registration step failed")
                return False
            
            # Step 2: Login
            login_response = requests.post(
                self.login_endpoint,
                json=register_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code != 200:
                self.record_result("Complete Auth Flow", False, "Login step failed")
                return False
            
            # Step 3: Try duplicate registration
            duplicate_response = requests.post(
                self.register_endpoint,
                json=register_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if duplicate_response.status_code == 409:
                self.record_result("Complete Auth Flow", True, "Full flow completed successfully")
                return True
            else:
                self.record_result("Complete Auth Flow", False, "Duplicate check failed")
                return False
                
        except Exception as e:
            self.record_result("Complete Auth Flow", False, f"Error: {e}")
            return False
    
    # Quiz Generation Tests
    def create_test_user(self):
        """Helper method to create a test user for quiz tests."""
        test_email = TEST_EMAIL_PREFIX + fake.email()
        test_password = fake.password(length=12)
        
        payload = {
            "mail": test_email,
            "password": test_password
        }
        
        try:
            response = requests.post(
                self.register_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                return test_email, test_password, payload
            else:
                return None, None, None
        except Exception:
            return None, None, None
    
    def create_sample_text_file(self):
        """Create a sample text file for testing."""
        sample_text = """
        Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines 
        that can perform tasks that typically require human intelligence. These tasks include learning, 
        reasoning, problem-solving, perception, and language understanding.
        
        Machine Learning is a subset of AI that focuses on the development of algorithms and statistical models 
        that enable computers to improve their performance on a specific task through experience without being 
        explicitly programmed.
        
        Deep Learning is a subset of machine learning that uses neural networks with multiple layers to model 
        and understand complex patterns in data. It has been particularly successful in areas such as image 
        recognition, natural language processing, and speech recognition.
        
        Natural Language Processing (NLP) is a field of AI that focuses on the interaction between computers 
        and humans through natural language. It involves developing algorithms and models that can understand, 
        interpret, and generate human language.
        """
        return sample_text.strip()
    
    def test_quiz_generation_practice_mode(self):
        """Test quiz generation in practice mode."""
        # Create test user first
        test_email, test_password, user_payload = self.create_test_user()
        if not test_email:
            self.record_result("Quiz Generation Practice Mode", False, "Failed to create test user")
            return False
        
        # Login to get user_id
        try:
            login_response = requests.post(
                self.login_endpoint,
                json=user_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code != 200:
                self.record_result("Quiz Generation Practice Mode", False, "Login failed")
                return False
            
            user_data = login_response.json()
            user_id = user_data.get('user_id')
            
            # Create sample text file
            sample_text = self.create_sample_text_file()
            
            # Prepare file upload
            files = {
                'file': ('test_document.txt', io.StringIO(sample_text), 'text/plain')
            }
            
            data = {
                'numQuestions': 3,
                'mode': 'practice',
                'userId': user_id,
                'quizTitle': 'AI Basics Test - Practice Mode'
            }
            
            # Generate quiz
            response = requests.post(
                self.generate_questions_endpoint,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 202:
                response_data = response.json()
                if 'jobId' in response_data:
                    self.record_result("Quiz Generation Practice Mode", True, "Practice quiz generation initiated successfully")
                    return True
                else:
                    self.record_result("Quiz Generation Practice Mode", False, "No jobId in response")
                    return False
            else:
                self.record_result("Quiz Generation Practice Mode", False, f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.record_result("Quiz Generation Practice Mode", False, f"Error: {e}")
            return False
    
    def test_quiz_generation_exam_mode(self):
        """Test quiz generation in exam mode."""
        # Create test user first
        test_email, test_password, user_payload = self.create_test_user()
        if not test_email:
            self.record_result("Quiz Generation Exam Mode", False, "Failed to create test user")
            return False
        
        # Login to get user_id
        try:
            login_response = requests.post(
                self.login_endpoint,
                json=user_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code != 200:
                self.record_result("Quiz Generation Exam Mode", False, "Login failed")
                return False
            
            user_data = login_response.json()
            user_id = user_data.get('user_id')
            
            # Create sample text file
            sample_text = self.create_sample_text_file()
            
            # Prepare file upload
            files = {
                'file': ('test_document.txt', io.StringIO(sample_text), 'text/plain')
            }
            
            data = {
                'numQuestions': 5,
                'duration': 30,  # 30 minutes for exam mode
                'mode': 'exam',
                'userId': user_id,
                'quizTitle': 'AI Basics Test - Exam Mode'
            }
            
            # Generate quiz
            response = requests.post(
                self.generate_questions_endpoint,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 202:
                response_data = response.json()
                if 'jobId' in response_data:
                    self.record_result("Quiz Generation Exam Mode", True, "Exam quiz generation initiated successfully")
                    return True
                else:
                    self.record_result("Quiz Generation Exam Mode", False, "No jobId in response")
                    return False
            else:
                self.record_result("Quiz Generation Exam Mode", False, f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.record_result("Quiz Generation Exam Mode", False, f"Error: {e}")
            return False
    
    def test_quiz_generation_missing_file(self):
        """Test quiz generation with missing file."""
        # Create test user first
        test_email, test_password, user_payload = self.create_test_user()
        if not test_email:
            self.record_result("Quiz Generation Missing File", False, "Failed to create test user")
            return False
        
        # Login to get user_id
        try:
            login_response = requests.post(
                self.login_endpoint,
                json=user_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            user_data = login_response.json()
            user_id = user_data.get('user_id')
            
            data = {
                'numQuestions': 3,
                'mode': 'practice',
                'userId': user_id,
                'quizTitle': 'Test Quiz'
            }
            
            # Try to generate quiz without file
            response = requests.post(
                self.generate_questions_endpoint,
                data=data,
                timeout=10
            )
            
            if response.status_code == 400:
                self.record_result("Quiz Generation Missing File", True, "Correctly rejected request without file")
                return True
            else:
                self.record_result("Quiz Generation Missing File", False, f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.record_result("Quiz Generation Missing File", False, f"Error: {e}")
            return False
    
    def test_quiz_generation_missing_user_id(self):
        """Test quiz generation with missing user ID."""
        try:
            # Create sample text file
            sample_text = self.create_sample_text_file()
            
            # Prepare file upload
            files = {
                'file': ('test_document.txt', io.StringIO(sample_text), 'text/plain')
            }
            
            data = {
                'numQuestions': 3,
                'mode': 'practice',
                'quizTitle': 'Test Quiz'
                # Missing userId
            }
            
            # Try to generate quiz without user_id
            response = requests.post(
                self.generate_questions_endpoint,
                files=files,
                data=data,
                timeout=10
            )
            
            if response.status_code == 400:
                response_data = response.json()
                if 'User ID is required' in response_data.get('error', ''):
                    self.record_result("Quiz Generation Missing User ID", True, "Correctly rejected request without user ID")
                    return True
                else:
                    self.record_result("Quiz Generation Missing User ID", False, "Wrong error message")
                    return False
            else:
                self.record_result("Quiz Generation Missing User ID", False, f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.record_result("Quiz Generation Missing User ID", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("=" * 70)
        print("QUIZ AI COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        # Health Tests
        self.log("HEALTH ENDPOINT TESTS", "SECTION")
        self.test_health_endpoint_exists()
        self.test_health_response_format()
        self.test_health_response_time()
        
        print()
        
        # Authentication Tests
        self.log("AUTHENTICATION TESTS", "SECTION")
        self.test_user_registration_success()
        self.test_user_registration_duplicate_email()
        self.test_user_registration_missing_fields()
        self.test_user_login_success()
        self.test_user_login_invalid_credentials()
        self.test_complete_auth_flow()
        
        print()
        
        # Quiz Generation Tests
        self.log("QUIZ GENERATION TESTS", "SECTION")
        self.test_quiz_generation_practice_mode()
        self.test_quiz_generation_exam_mode()
        self.test_quiz_generation_missing_file()
        self.test_quiz_generation_missing_user_id()
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total:  {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n🎉 All tests passed! Your Quiz AI API is working correctly.")
            return True
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Please check the server and database.")
            return False

if __name__ == "__main__":
    tester = QuizAITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
