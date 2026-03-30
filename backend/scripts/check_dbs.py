import pyodbc
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SERVER = os.getenv('DB_HOST', '192.168.1.232')
USER = os.getenv('DB_USER', 'ccalidad')
PASSWORD = os.getenv('DB_PASSWORD', 'Plf2025**')
DRIVER = '{ODBC Driver 13 for SQL Server}'

conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={PASSWORD};DATABASE=master;TrustServerCertificate=yes;Encrypt=no;'

print(f"--- Checking Databases on {SERVER} ---")
try:
    conn = pyodbc.connect(conn_str, timeout=5)
    cursor = conn.cursor()
    
    # List databases starting with POSTVENTA or PRDPOSTVENTA
    cursor.execute("SELECT name, create_date FROM sys.databases WHERE name LIKE '%POSTVENTA%' ORDER BY name")
    
    rows = cursor.fetchall()
    
    if rows:
        print("\n[YES] Found these databases:")
        for row in rows:
            print(f" - {row.name} (Created: {row.create_date})")
    else:
        print("\n[NO] No databases found matching 'POSTVENTA%'")

    conn.close()

except Exception as e:
    print(f"\n[ERROR] Error connecting to master: {e}")
