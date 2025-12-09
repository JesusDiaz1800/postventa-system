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
        print("🔧 Fixing users table id column type...")
        
        # First, check current type
        cursor.execute("""
            SELECT DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'id'
        """)
        current_type = cursor.fetchone()[0]
        print(f"Current id type: {current_type}")
        
        if current_type == 'int':
            print("Converting id from int to bigint...")
            
            # Create a new column with bigint type
            cursor.execute("ALTER TABLE users ADD id_new bigint IDENTITY(1,1)")
            
            # Copy data from old id to new id
            cursor.execute("UPDATE users SET id_new = id")
            
            # Drop the old id column
            cursor.execute("ALTER TABLE users DROP COLUMN id")
            
            # Rename the new column to id
            cursor.execute("EXEC sp_rename 'users.id_new', 'id', 'COLUMN'")
            
            # Make it primary key
            cursor.execute("ALTER TABLE users ADD PRIMARY KEY (id)")
            
            print("✅ Users table id column converted to bigint")
        else:
            print("✅ Users table id column is already bigint")
        
        # Verify the change
        cursor.execute("""
            SELECT DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'id'
        """)
        new_type = cursor.fetchone()[0]
        print(f"New id type: {new_type}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
