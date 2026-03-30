import pyodbc

def extract_tn_super():
    server = 'localhost\\SQLEXPRESS'
    database = 'TSTPOLPERU'
    conn_str = f'DRIVER={{ODBC Driver 13 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes;'
    
    try:
        print(f"Connecting to {database} via Windows Auth for SP extraction...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        cursor.execute("EXEC sp_helptext 'SBO_SP_TransactionNotification'")
        lines = cursor.fetchall()
        
        full_text = "".join([l[0] for l in lines])
        
        with open('peru_tn_full.sql', 'w', encoding='utf-8') as f:
            f.write(full_text)
        print("Success: TN extracted to peru_tn_full.sql")
        
        # Buscar validación de Service Call (191)
        import re
        match = re.search(r"(@object_type\s*=\s*'191')", full_text, re.IGNORECASE)
        if match:
            start = match.start()
            print("Found 191 section:")
            print(full_text[start:start+1000])
        else:
            print("Section for 191 not found in raw search.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_tn_super()
