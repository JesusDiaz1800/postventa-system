import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections

def test_co_connection():
    db_alias = 'sap_db_co'
    print(f"Testing connection to alias: {db_alias}")
    
    try:
        connection = connections[db_alias]
        with connection.cursor() as cursor:
            # Query the database name to verify we are where we think we are
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            print(f"Successfully connected to SQL Server!")
            print(f"Current Database: {db_name}")
            
            if db_name.upper() == 'TSTPOLCOLOMBIA_2':
                print("SUCCESS: Connected to the correct test database.")
            else:
                print(f"WARNING: Connected to {db_name} instead of TSTPOLCOLOMBIA_2.")
            
            # Test a common table
            cursor.execute("SELECT TOP 1 CardCode, CardName FROM OCRD")
            row = cursor.fetchone()
            if row:
                print(f"Master Data Sample: {row[0]} - {row[1]}")
            
    except Exception as e:
        print(f"ERROR: Could not connect to {db_alias}")
        print(str(e))

if __name__ == "__main__":
    test_co_connection()
