"""
Script para verificar la relación entre OSCL.contctCode y OCPR (tabla de contactos)
"""
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
    
    print("Consultando contact code 4957...")
    
    # Query con JOIN para obtener nombre del contacto
    cursor.execute("""
        SELECT 
            sc.callID,
            sc.subject,
            sc.contctCode,
            cp.Name as ContactName,
            cp.Tel1,
            cp.Cellolar
        FROM OSCL sc
        LEFT JOIN OCPR cp ON sc.contctCode = cp.CntctCode
        WHERE sc.callID = 26531
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"\nCallID: {row[0]}")
        print(f"Subject: {row[1]}")
        print(f"contctCode: {row[2]}")
        print(f"Contact Name: {row[3]}")
        print(f"Tel1: {row[4]}")
        print(f"Cellolar: {row[5]}")
    else:
        print("No se encontró el registro")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
