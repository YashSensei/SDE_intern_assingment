"""
Deploy schema and seed data to NeonDB
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', 5432)
    )

def execute_sql_file(cursor, filepath):
    """Execute SQL commands from a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    cursor.execute(sql_content)

def reset_database(cursor, conn):
    """Reset database by dropping all tables"""
    try:
        print("\n🗑️  Resetting database (dropping existing tables)...")
        execute_sql_file(cursor, 'sql/reset_db.sql')
        conn.commit()
        print("✅ Database reset successfully!")
    except Exception as e:
        print(f"⚠️  Reset warning (tables may not exist): {e}")
        conn.rollback()

def main():
    print("🚀 Deploying Database Schema and Seed Data to NeonDB")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\n📡 Connecting to NeonDB...")
        conn = get_db_connection()
        conn.autocommit = False
        cursor = conn.cursor()
        print("✅ Connected successfully!")
        
        # Reset database first
        reset_database(cursor, conn)
        
        # Deploy schema
        print("\n📋 Deploying schema.sql...")
        execute_sql_file(cursor, 'sql/schema.sql')
        conn.commit()
        print("✅ Schema deployed successfully!")
        
        # Deploy seed data
        print("\n🌱 Deploying seed.sql...")
        execute_sql_file(cursor, 'sql/seed.sql')
        conn.commit()
        print("✅ Seed data deployed successfully!")
        
        # Fetch verification data
        print("\n📊 Database Statistics:")
        print("-" * 60)
        cursor.execute("""
            SELECT 'Departments' AS table_name, COUNT(*) AS record_count FROM departments
            UNION ALL
            SELECT 'Students', COUNT(*) FROM students
            UNION ALL
            SELECT 'Courses', COUNT(*) FROM courses
            UNION ALL
            SELECT 'Enrollments', COUNT(*) FROM enrollments;
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]:<20} : {row[1]:>5} records")
        
        print("-" * 60)
        print("\n✅ Deployment completed successfully!")
        print("🎉 Database is ready for use!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error during deployment: {e}")
        if conn:
            conn.rollback()
        raise

if __name__ == "__main__":
    main()
