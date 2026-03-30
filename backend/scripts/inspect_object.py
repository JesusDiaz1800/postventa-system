import pyodbc
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SERVER = '192.168.1.232'
USER = 'ccalidad'
# Try Plf2025** (lowercase l)
PASSWORD = 'Plf2025**' 
DATABASE = 'POSTVENTA_PE'
DRIVER = '{ODBC Driver 13 for SQL Server}'

conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={PASSWORD};DATABASE={DATABASE};TrustServerCertificate=yes;Encrypt=no;'

print(f"--- INSPECTING {DATABASE} for 'notification_categories' ---")

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()

    cursor.execute("SELECT name, type_desc FROM sys.objects WHERE name = 'notification_categories'")
    row = cursor.fetchone()
    
    if row:
        print(f"[FOUND] Name: {row.name}, Type: {row.type_desc}")
    else:
        print("[NOT FOUND] The object does not exist.")

    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
