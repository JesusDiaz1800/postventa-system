import os
import sys
import django
import pyodbc
from django.conf import settings

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connection

def check_physical_columns():
    with connection.cursor() as cursor:
        # Listar todas las tablas
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in DB: {tables}")
        
        target_table = 'documents_documentattachment'
        if target_table in tables:
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{target_table}'")
            columns = [row[0] for row in cursor.fetchall()]
            print(f"Physical columns in {target_table}: {columns}")
            
            if 'section' not in columns:
                print("CRITICAL: 'section' is missing physically!")
            else:
                print("'section' exists physically.")
        else:
            print(f"ERROR: Table {target_table} not found!")

if __name__ == '__main__':
    check_physical_columns()
