import pyodbc
import os
from dotenv import load_dotenv

# Load env to get credentials
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SERVER = os.getenv('DB_HOST', '192.168.1.232')
USER = os.getenv('DB_USER', 'ccalidad')
PASSWORD = os.getenv('DB_PASSWORD', 'Plf2025**')
DRIVER = '{ODBC Driver 13 for SQL Server}'
DATABASE = 'POSTVENTA_PE'

conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={PASSWORD};DATABASE={DATABASE};TrustServerCertificate=yes;Encrypt=no;'

print(f"--- Connection Test: {DATABASE} ---")
print(f"Target: {SERVER}")
print(f"User: {USER}")

try:
    conn = pyodbc.connect(conn_str, timeout=5)
    print("[SUCCESS] Connected to database!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT DB_NAME()")
    row = cursor.fetchone()
    print(f"Current DB: {row[0]}")
    conn.close()
    
except Exception as e:
    print("[FAILURE] Could not connect.")
    print(f"Error: {e}")
