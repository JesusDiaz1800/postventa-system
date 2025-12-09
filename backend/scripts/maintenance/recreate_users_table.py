#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        print("🔧 Recreating users table with correct data types...")
        
        # Get current users data
        cursor.execute("SELECT * FROM users")
        users_data = cursor.fetchall()
        
        # Get column names
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users'
            ORDER BY ORDINAL_POSITION
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(users_data)} users to preserve")
        
        # Drop the existing table
        cursor.execute("DROP TABLE users")
        print("✅ Dropped existing users table")
        
        # Recreate with correct structure
        cursor.execute("""
            CREATE TABLE users (
                id bigint IDENTITY(1,1) PRIMARY KEY,
                password nvarchar(128) NOT NULL,
                last_login datetime2 NULL,
                is_superuser bit NOT NULL DEFAULT 0,
                username nvarchar(150) NOT NULL UNIQUE,
                first_name nvarchar(150) NOT NULL,
                last_name nvarchar(150) NOT NULL,
                email nvarchar(254) NOT NULL,
                is_staff bit NOT NULL DEFAULT 0,
                is_active bit NOT NULL DEFAULT 1,
                date_joined datetime2 NOT NULL DEFAULT GETDATE(),
                role nvarchar(50) NOT NULL DEFAULT 'user',
                created_at datetime2 NOT NULL DEFAULT GETDATE(),
                updated_at datetime2 NOT NULL DEFAULT GETDATE(),
                phone nvarchar(20) NOT NULL DEFAULT '',
                department nvarchar(100) NOT NULL DEFAULT ''
            )
        """)
        print("✅ Created new users table with correct structure")
        
        # Insert the data back
        for user_data in users_data:
            # Map the data to new structure
            insert_sql = """
                INSERT INTO users (password, last_login, is_superuser, username, first_name, last_name, 
                                 email, is_staff, is_active, date_joined, role, created_at, updated_at, phone, department)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 'admin', GETDATE(), GETDATE(), '', '')
            """
            cursor.execute(insert_sql, user_data[1:])  # Skip the old id
        
        print("✅ Restored user data")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"✅ Users table now has {count} records")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
