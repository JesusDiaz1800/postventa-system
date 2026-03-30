import pyodbc

conn_str = (
    'DRIVER={SQL Server};'
    'SERVER=192.168.1.34;'
    'DATABASE=SBO_POLIFUSION;'
    'UID=sa;'
    'PWD=Polifusion2024'
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("Searching for UDFs in OSCL table related to 'Estado' or 'Visita'...")
    query = """
        SELECT AliasID, Descr 
        FROM CUFD 
        WHERE TableID = 'OSCL' 
        AND (AliasID LIKE '%Estado%' OR AliasID LIKE '%Visita%' 
             OR Descr LIKE '%Estado%' OR Descr LIKE '%Visita%')
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        print("No matching UDFs found. Listing ALL UDFs for OSCL:")
        cursor.execute("SELECT AliasID, Descr FROM CUFD WHERE TableID = 'OSCL'")
        rows = cursor.fetchall()

    for alias, descr in rows:
        print(f"U_{alias}: {descr}")
        
    print("\nChecking current values of these UDFs for DocNum 24919 (from latest screenshot):")
    if rows:
        cols = [f"U_{r[0]}" for r in rows]
        # Check standard status too
        cols.append("status")
        
        query_data = f"SELECT {', '.join(cols)} FROM OSCL WHERE DocNum = 24919"
        try:
            cursor.execute(query_data)
            row = cursor.fetchone()
            if row:
                for col, val in zip(cols, row):
                    print(f"{col}: {val}")
            else:
                print("DocNum 24919 not found.")
        except Exception as e:
            print(f"Error querying data: {e}")

    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
