#!/usr/bin/env python3

import os
import sys
import subprocess

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'flask', 'mysql-connector-python', 'bcrypt', 'python-dotenv',
        'PyPDF2', 'requests', 'beautifulsoup4', 'youtube-transcript-api',
        'reportlab'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\\nInstall them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_database():
    """Check database connection"""
    try:
        from db import get_connection
        conn = get_connection()
        conn.close()
        print("[OK] Database connection successful")
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        print("Please check your database configuration in .env file")
        return False

def main():
    print("=== EduSynth AI Startup ===\\n")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("[ERROR] app.py not found. Please run this from the project directory.")
        return
    
    # Check requirements
    print("Checking requirements...")
    if not check_requirements():
        return
    
    # Check database
    print("Checking database connection...")
    if not check_database():
        return
    
    # Start the application
    print("\\n[INFO] Starting EduSynth AI...")
    print("The application will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server\\n")
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        print("\\n[INFO] Server stopped by user")
    except Exception as e:
        print(f"\\n[ERROR] Failed to start server: {e}")

if __name__ == "__main__":
    main()