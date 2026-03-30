import pyodbc
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SERVER = '192.168.1.232'
USER = 'ccalidad'
# Use the known working password
PASSWORD = 'Plf2025**' 
DATABASE = 'POSTVENTA_CO'
DRIVER = '{ODBC Driver 13 for SQL Server}'

def test_connection():
    print(f"Testing connection to {DATABASE} on {SERVER}...")
    try:
        conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={PASSWORD};DATABASE={DATABASE};TrustServerCertificate=yes;Encrypt=no;'
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        row = cursor.fetchone()
        print(f"[SUCCESS] Connected to database: {row[0]}")
        
        # Check permissions by trying to create a temp table?
        # Or just assume if we can connect we're good?
        # Let's check current user
        cursor.execute("SELECT CURRENT_USER")
        user = cursor.fetchone()[0]
        print(f"[INFO] Current User: {user}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
