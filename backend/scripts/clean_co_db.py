import pyodbc
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SERVER = '192.168.1.232'
USER = 'ccalidad'
PASSWORD = 'Plf2025**' 
DATABASE = 'POSTVENTA_CO'
DRIVER = '{ODBC Driver 13 for SQL Server}'

def get_connection():
    conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={PASSWORD};DATABASE={DATABASE};TrustServerCertificate=yes;Encrypt=no;'
    return pyodbc.connect(conn_str, timeout=10)

print(f"--- CLEANING DATABASE {DATABASE} ---")
print("WARNING: This will DROP ALL TABLES in this database.")

try:
    # Enable Autocommit to ensure drops are immediate
    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    # CRITICAL SAFETY CHECK
    cursor.execute("SELECT DB_NAME()")
    current_db = cursor.fetchone()[0]
    print(f"CONNECTED TO: {current_db}")
    
    if current_db.lower() != 'postventa_co':
        print(f"[FATAL ERROR] Refusing to clean. Connected to '{current_db}' instead of 'POSTVENTA_CO'.")
        conn.close()
        exit(1)
        
    print("[SAFETY CHECK PASSED] Target is correct.")

    # 1. DROP ALL FOREIGN KEY CONSTRAINTS
    print("Dropping Foreign Key Constraints...")
    cursor.execute("""
        SELECT 
            fk.name AS ForeignKeyName,
            t.name AS TableName
        FROM sys.foreign_keys fk
        INNER JOIN sys.tables t ON fk.parent_object_id = t.object_id
    """)
    constraints = cursor.fetchall()
    
    for fk_name, table_name in constraints:
        try:
            cursor.execute(f"ALTER TABLE [{table_name}] DROP CONSTRAINT [{fk_name}]")
            print(f" - Dropped Constraint: {fk_name}")
        except Exception as e:
            print(f" ! Error dropping constraint {fk_name}: {e}")

    # 2. DROP ALL TABLES (Using sys.objects for reliability)
    print("Dropping tables...")
    cursor.execute("SELECT name FROM sys.objects WHERE type = 'U'")
    tables = [row.name for row in cursor.fetchall()]
    
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE [{table}]")
            print(f" - Dropped Table: {table}")
        except Exception as e:
            print(f" ! Error dropping table {table}: {e}")

    # 3. VERIFICATION
    cursor.execute("SELECT COUNT(*) FROM sys.objects WHERE type = 'U'")
    remaining = cursor.fetchone()[0]
    
    if remaining == 0:
        print("\n[SUCCESS] Database cleaned successfully. Users Tables count: 0")
    else:
        print(f"\n[WARNING] Cleanup incomplete. {remaining} tables remain.")

    conn.close()

except Exception as e:
    print(f"\n[CRITICAL ERROR] {e}")
