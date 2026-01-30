import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        # Use DATABASE_URL for production (Render) or local config for development
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            # Production: Parse DATABASE_URL
            import urllib.parse as urlparse
            url = urlparse.urlparse(database_url)
            return mysql.connector.connect(
                host=url.hostname,
                port=url.port or 3306,
                user=url.username,
                password=url.password,
                database=url.path[1:]
            )
        else:
            # Development: Use individual environment variables
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "root"),
                database=os.getenv("DB_NAME", "Automated_Educational")
            )
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        raise
