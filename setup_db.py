import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    try:
        # Connect without database first
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root")
        )
        
        cur = conn.cursor()
        
        # Create database if it doesn't exist
        db_name = os.getenv("DB_NAME", "Automated_Educational")
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cur.execute(f"USE {db_name}")
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                mobile VARCHAR(20),
                college VARCHAR(255),
                branch VARCHAR(255),
                year VARCHAR(50),
                language VARCHAR(50),
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_activity table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                activity_type ENUM('PDF', 'YouTube', 'Website', 'Quiz') NOT NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database setup completed successfully!")
        return True
        
    except mysql.connector.Error as e:
        print(f"Database setup error: {e}")
        return False

if __name__ == "__main__":
    setup_database()