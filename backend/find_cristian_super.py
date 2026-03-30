import pyodbc

def find_cristian_super():
    server = 'localhost\\SQLEXPRESS'
    database = 'TSTPOLCOLOMBIA_2'
    conn_str = f'DRIVER={{ODBC Driver 13 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes;'
    
    try:
        print(f"Connecting to {database} via Windows Auth for final search...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Búsqueda amplia en OHEM
        print("Searching OHEM...")
        cursor.execute("SELECT empID, firstName, lastName FROM OHEM WHERE firstName LIKE '%Cristian%' OR lastName LIKE '%Peña%'")
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                print(f"FOUND IN OHEM: ID={r[0]}, Name={r[1]} {r[2]}")
        else:
            print("Not found in OHEM.")
            
        # Búsqueda en OUSR (Usuarios)
        print("Searching OUSR...")
        cursor.execute("SELECT USERID, USER_CODE, U_NAME FROM OUSR WHERE U_NAME LIKE '%Cristian%'")
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                print(f"FOUND IN OUSR: ID={r[0]}, Code={r[1]}, Name={r[2]}")
                
        # Búsqueda en OSLP (Vendedores)
        print("Searching OSLP...")
        cursor.execute("SELECT SlpCode, SlpName FROM OSLP WHERE SlpName LIKE '%Cristian%'")
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                print(f"FOUND IN OSLP: ID={r[0]}, Name={r[1]}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_cristian_super()
