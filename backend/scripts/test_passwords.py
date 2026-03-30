import pyodbc
import os

SERVER = '192.168.1.232'
USER = 'ccalidad'
DATABASE = 'POSTVENTA_PE'
DRIVER = '{ODBC Driver 13 for SQL Server}'

PASSWORDS = [
    'Plf2025**',  # From .env (Current)
    'PLf2025**',  # From User Chat (Potential Typo or Real)
]

print(f"--- Credential Test for {DATABASE} @ {SERVER} ---")

for pwd in PASSWORDS:
    print(f"\nTesting password: {pwd}")
    conn_str = f'DRIVER={DRIVER};SERVER={SERVER};UID={USER};PWD={pwd};DATABASE={DATABASE};TrustServerCertificate=yes;Encrypt=no;'
    
    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        print("[SUCCESS] Connected.")
        conn.close()
        break
    except Exception as e:
        print("[FAILED]")
        # print(e) # Keep clean output

print("\n--- End Test ---")
