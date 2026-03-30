import pyodbc
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SERVER = '192.168.1.232'
USER = 'ccalidad'
# Try both passwords directly
DATABASE = 'POSTVENTA_PE'
DRIVER = '{ODBC Driver 13 for SQL Server}'

def get_connection(pwd):
    conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={pwd};DATABASE={DATABASE};TrustServerCertificate=yes;Encrypt=no;'
    return pyodbc.connect(conn_str, timeout=5)

print(f"--- Inspecting {DATABASE} ---")

conn = None
try:
    conn = get_connection('Plf2025**')
except:
    try:
        conn = get_connection('PLf2025**')
    except Exception as e:
        print(f"[FATAL] Could not connect with either password: {e}")
        exit(1)

cursor = conn.cursor()

# 1. List Tables
print("\n[TABLES FOUND]")
cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
tables = [row.TABLE_NAME for row in cursor.fetchall()]

if not tables:
    print(" - <EMPTY DATABASE>")
else:
    for t in tables:
        print(f" - {t}")

# 2. Check Data in Key Tables
if 'auth_user' in tables:
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    count = cursor.fetchone()[0]
    print(f"\n[DATA CHECK] auth_user rows: {count}")
else:
    print("\n[DATA CHECK] auth_user table NOT found.")

conn.close()
