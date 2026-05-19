import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def check_databases():
    host = os.getenv('DB_HOST', '192.168.1.232')
    user = os.getenv('DB_USER', 'ccalidad')
    password = os.getenv('DB_PASSWORD', 'Plf2025**')
    driver = os.getenv('ODBC_DRIVER', 'SQL Server Native Client 11.0')
    
    # We try to connect to 'master' to list other DBs
    conn_str = f'DRIVER={{{driver}}};SERVER={host};DATABASE=master;UID={user};PWD={password};Encrypt=no;TrustServerCertificate=yes;'
    
    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE name LIKE 'SERTEC_%' OR name LIKE 'PRDPOSTVENTA_%'")
        dbs = [row.name for row in cursor.fetchall()]
        print("Bases de datos encontradas:")
        for db in dbs:
            print(f"- {db}")
        conn.close()
    except Exception as e:
        print(f"Error al conectar al servidor SQL ({host}): {e}")

if __name__ == "__main__":
    check_databases()
