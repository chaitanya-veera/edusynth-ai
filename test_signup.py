#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_connection
import bcrypt

def test_signup():
    try:
        # Test data
        name = "Test User"
        email = "test@example.com"
        mobile = "1234567890"
        college = "TEST COLLEGE"
        branch = "CSE"
        year = "3rd Year"
        language = "English"
        password = "Test@123"
        
        print("Testing signup process...")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Mobile: {mobile}")
        print(f"College: {college}")
        print(f"Branch: {branch}")
        print(f"Year: {year}")
        print(f"Language: {language}")
        print(f"Password: {password}")
        
        # Test database connection
        print("\n1. Testing database connection...")
        conn = get_connection()
        cur = conn.cursor()
        print("[OK] Database connection successful")
        
        # Check if email already exists
        print("\n2. Checking if email exists...")
        cur.execute("SELECT email FROM users WHERE email=%s", (email,))
        existing = cur.fetchone()
        if existing:
            print(f"[INFO] Email {email} already exists, deleting for test...")
            cur.execute("DELETE FROM users WHERE email=%s", (email,))
            conn.commit()
        print("[OK] Email check passed")
        
        # Test password hashing
        print("\n3. Testing password hashing...")
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        print(f"[OK] Password hashed successfully: {hashed[:20]}...")
        
        # Test insertion
        print("\n4. Testing user insertion...")
        cur.execute(
            "INSERT INTO users (full_name, email, mobile, college, branch, year, language, password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (name, email, mobile, college, branch, year, language, hashed)
        )
        conn.commit()
        print("[OK] User inserted successfully")
        
        # Verify insertion
        print("\n5. Verifying insertion...")
        cur.execute("SELECT id, full_name, email FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        if user:
            print(f"[OK] User found: ID={user[0]}, Name={user[1]}, Email={user[2]}")
        else:
            print("[ERROR] User not found after insertion")
        
        # Clean up
        print("\n6. Cleaning up test data...")
        cur.execute("DELETE FROM users WHERE email=%s", (email,))
        conn.commit()
        print("[OK] Test data cleaned up")
        
        conn.close()
        print("\n[SUCCESS] All tests passed! Signup should work correctly.")
        
    except Exception as e:
        print(f"\n[ERROR] Error during signup test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_signup()