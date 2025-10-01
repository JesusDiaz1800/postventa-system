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
        # Check users table structure
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users'
            ORDER BY ORDINAL_POSITION
        """)
        
        print("📋 Users table structure:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} ({row[2] if row[2] else 'N/A'}) - Nullable: {row[3]}")
        
        # Check if users table exists
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"\n✅ Users table has {count} records")
        
        # Check incidents table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'incidents'
        """)
        incidents_exists = cursor.fetchone()[0] > 0
        print(f"📋 Incidents table exists: {incidents_exists}")
        
        if incidents_exists:
            cursor.execute("SELECT COUNT(*) FROM incidents")
            count = cursor.fetchone()[0]
            print(f"✅ Incidents table has {count} records")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
