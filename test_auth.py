#!/usr/bin/env python3

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test@123"
TEST_NAME = "Test User"

def test_signup():
    """Test user registration"""
    print("Testing signup...")
    
    signup_data = {
        "user": TEST_NAME,
        "user_email": TEST_EMAIL,
        "user_mobile": "1234567890",
        "college": "TEST COLLEGE",
        "branch": "CSE",
        "year": "3rd Year",
        "language": "English",
        "user_pass": TEST_PASSWORD,
        "user_cpass": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/signupgo", data=signup_data, allow_redirects=False)
        if response.status_code == 302:  # Redirect means success
            print("[OK] Signup successful")
            return True
        else:
            print(f"[ERROR] Signup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Signup request failed: {e}")
        return False

def test_login():
    """Test user login"""
    print("Testing login...")
    
    login_data = {
        "user_email": TEST_EMAIL,
        "user_pass": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/logingo", data=login_data, allow_redirects=False)
        if response.status_code == 302:  # Redirect means success
            print("[OK] Login successful")
            return True
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Login request failed: {e}")
        return False

def test_forgot_password():
    """Test forgot password functionality"""
    print("Testing forgot password...")
    
    forgot_data = {"email": TEST_EMAIL}
    
    try:
        response = requests.post(f"{BASE_URL}/forgot", 
                               json=forgot_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("[OK] Forgot password request successful")
                return True
            else:
                print(f"[ERROR] Forgot password failed: {result.get('message')}")
                return False
        else:
            print(f"[ERROR] Forgot password request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Forgot password request failed: {e}")
        return False

def main():
    print("=== Authentication System Test ===\\n")
    
    print("Make sure the Flask app is running on http://localhost:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    # Test signup
    signup_success = test_signup()
    time.sleep(1)
    
    # Test login (only if signup succeeded)
    if signup_success:
        login_success = test_login()
        time.sleep(1)
        
        # Test forgot password
        forgot_success = test_forgot_password()
        
        print("\\n=== Test Results ===")
        print(f"Signup: {'PASS' if signup_success else 'FAIL'}")
        print(f"Login: {'PASS' if login_success else 'FAIL'}")
        print(f"Forgot Password: {'PASS' if forgot_success else 'FAIL'}")
        
        if all([signup_success, login_success, forgot_success]):
            print("\\n[SUCCESS] All authentication functions working!")
        else:
            print("\\n[WARNING] Some functions need attention")
    else:
        print("\\n[ERROR] Cannot test other functions - signup failed")

if __name__ == "__main__":
    main()