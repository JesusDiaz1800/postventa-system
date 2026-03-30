import pyodbc

def find_cristian_direct():
    server = 'localhost\\SQLEXPRESS'
    database = 'TSTPOLCOLOMBIA_2'
    # Usar ODBC Driver 13 for SQL Server
    conn_str = f'DRIVER={{ODBC Driver 13 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes;'
    
    try:
        print(f"Connecting to {database} via Windows Auth...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        query = "SELECT EmpID, firstName, lastName, JobTitle, Role FROM OHEM WHERE firstName LIKE ? OR lastName LIKE ?"
        cursor.execute(query, ('%Cristian%', '%Peña%'))
        rows = cursor.fetchall()
        
        if not rows:
            # Reintento sin la ñ por si acaso
            cursor.execute("SELECT EmpID, firstName, lastName, JobTitle, Role FROM OHEM WHERE firstName LIKE ? OR lastName LIKE ?", ('%Cristian%', '%Pena%'))
            rows = cursor.fetchall()
            
        if not rows:
            print("No se encontró a Cristian Peña")
        else:
            for row in rows:
                print(f"ID: {row[0]}, Nombre: {row[1]} {row[2]}, Cargo: {row[3]}, Role: {row[4]}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    find_cristian_direct()
