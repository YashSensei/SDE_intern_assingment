"""
Database connection test script for NeonDB
Tests connectivity and basic operations
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

# Load environment variables
load_dotenv()

def get_db_connection():
    """
    Creates and returns a database connection
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', 5432)
        )
        return connection
    except OperationalError as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def test_connection():
    """
    Tests database connection and basic query
    """
    print("🔄 Testing NeonDB connection...")
    print("-" * 50)
    
    # Get connection
    conn = get_db_connection()
    
    if conn is None:
        print("❌ Connection failed. Please check your credentials in .env file.")
        return False
    
    try:
        # Create cursor
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("✅ Successfully connected to NeonDB!")
        print(f"📊 PostgreSQL version: {db_version[0]}")
        
        # Get database name
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"📁 Connected to database: {db_name[0]}")
        
        # Get current user
        cursor.execute("SELECT current_user;")
        db_user = cursor.fetchone()
        print(f"👤 Connected as user: {db_user[0]}")
        
        # Close cursor
        cursor.close()
        
        print("-" * 50)
        print("✅ Connection test PASSED!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error executing test query: {e}")
        return False
        
    finally:
        if conn:
            conn.close()
            print("🔌 Connection closed.")

if __name__ == "__main__":
    success = test_connection()
    
    if not success:
        print("\n⚠️  TROUBLESHOOTING:")
        print("1. Verify .env file exists with correct credentials")
        print("2. Check NeonDB dashboard for connection string")
        print("3. Ensure your IP is not blocked by NeonDB")
        print("4. Confirm database is active (not paused)")
