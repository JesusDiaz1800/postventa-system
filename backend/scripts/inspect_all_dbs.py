import pyodbc
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SERVER = '192.168.1.232'
USER = 'ccalidad'
PASSWORD = 'Plf2025**' 
DRIVER = '{ODBC Driver 13 for SQL Server}'

DATABASES_TO_CHECK = [
    'postventa_system', 
    'POSTVENTA_PE',
    'POSTVENTA_CO'
]

print("--- MULTI-DATABASE INSPECTOR ---")

for db in DATABASES_TO_CHECK:
    print(f"\n[CHECKING] {db}...")
    try:
        conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={PASSWORD};DATABASE={db};TrustServerCertificate=yes;Encrypt=no;'
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DB_NAME()")
        actual_db = cursor.fetchone()[0]
        print(f" -> Connected to: {actual_db}")

        # Check for core users table
        cursor.execute("SELECT name, type_desc, create_date FROM sys.objects WHERE name = 'users'")
        row = cursor.fetchone()
        
        if row:
            print(f" -> [OK] Table 'users' FOUND (Created: {row.create_date})")
        else:
            print(f" -> [MISSING] Table 'users' NOT found.")
            
        conn.close()

    except Exception as e:
        print(f" -> [ERROR] {e}")
