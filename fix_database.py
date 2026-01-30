#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_connection
import bcrypt

def fix_database():
    """Fix database issues and ensure proper table structure"""
    try:
        print("Fixing database issues...")
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Drop and recreate users table with correct structure
        print("Recreating users table...")
        cur.execute("DROP TABLE IF EXISTS user_activity")
        cur.execute("DROP TABLE IF EXISTS users")
        
        # Create users table
        cur.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                mobile VARCHAR(20) NOT NULL,
                college VARCHAR(255) NOT NULL,
                branch VARCHAR(255) NOT NULL,
                year VARCHAR(50) NOT NULL,
                language VARCHAR(50) NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_activity table
        cur.execute("""
            CREATE TABLE user_activity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                activity_type VARCHAR(50) NOT NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        print("[OK] Tables created successfully")
        
        # Test insert a sample user
        print("Testing user insertion...")
        test_email = "test@example.com"
        test_password = "Test@123"
        hashed = bcrypt.hashpw(test_password.encode(), bcrypt.gensalt()).decode('utf-8')
        
        cur.execute("""
            INSERT INTO users (full_name, email, mobile, college, branch, year, language, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, ("Test User", test_email, "1234567890", "Test College", "CSE", "3rd Year", "English", hashed))
        
        conn.commit()
        print("[OK] Test user inserted")
        
        # Verify and clean up
        cur.execute("SELECT id, full_name, email FROM users WHERE email=%s", (test_email,))
        user = cur.fetchone()
        if user:
            print(f"[OK] User verified: {user}")
            cur.execute("DELETE FROM users WHERE email=%s", (test_email,))
            conn.commit()
            print("[OK] Test user cleaned up")
        
        conn.close()
        print("\n[SUCCESS] Database fixed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_database()