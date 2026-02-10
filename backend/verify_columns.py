"""
Verificar columnas problemTyp y contctCode en OSCL
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
    
    print("Verificando columnas en OSCL...")
    
    # Verificar si existen las columnas
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'OSCL' 
        AND COLUMN_NAME IN ('problemTyp', 'ProblemTyp', 'contctCode')
        ORDER BY COLUMN_NAME
    """)
    
    print("\nColumnas encontradas:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}")
    
    # Obtener datos de ejemplo
    cursor.execute("""
        SELECT TOP 3 callID, problemTyp, contctCode 
        FROM OSCL 
        WHERE callID IS NOT NULL 
        ORDER BY callID DESC
    """)
    
    print("\nDatos de ejemplo:")
    for row in cursor.fetchall():
        print(f"  CallID: {row[0]}, problemTyp: {row[1]}, contctCode: {row[2]}")
    
    cursor.close()
    conn.close()
    print("\nOK - Columnas verificadas")
    
except Exception as e:
    print(f"Error: {e}")
