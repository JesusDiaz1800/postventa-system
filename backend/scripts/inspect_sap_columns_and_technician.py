import pyodbc
import json
from datetime import date, datetime

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

conn_str = (
    'DRIVER={SQL Server Native Client 11.0};'
    'SERVER=192.168.1.232;'
    'DATABASE=PRDPOLIFUSION;'
    'UID=ccalidad;'
    'PWD=Plf2025**;'
    'Encrypt=no;TrustServerCertificate=yes;ApplicationIntent=ReadOnly;'
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    print("--- 1. BUSCANDO COLUMNAS 'U_NX_%' y 'U_PROF%' EN OSCL ---")
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'OSCL' 
        AND (COLUMN_NAME LIKE 'U_NX_%' OR COLUMN_NAME LIKE 'U_PROF%' OR COLUMN_NAME LIKE 'U_ITO%' OR COLUMN_NAME LIKE 'U_OTROS%')
        ORDER BY COLUMN_NAME
    """)
    columns = [row.COLUMN_NAME for row in cursor.fetchall()]
    print("Columnas encontradas:", columns)
    
    print("\n--- 2. VERIFICANDO VALOR DE 'technician' EN UNA LLAMADA RECIENTE ---")
    cursor.execute("SELECT TOP 5 callID, technician, COALESCE(U_NX_VENDEDOR, 'N/A') as Vend FROM OSCL ORDER BY callID DESC")
    rows = cursor.fetchall()
    for row in rows:
        print(f"CallID: {row[0]}, Technician: {row[1]}, Vend: {row[2]}")
        
    print("\n--- 3. BUSCANDO TABLA DE EMPLEADOS (OHEM) O USUARIOS (OUSR) PARA MAPEAR TECNICO ---")
    # Check OHEM
    try:
        # Assuming technician field holds the ID. Usually it is empID.
        # Let's check a specific ID if we found one above, typically just check if table exists and has names.
        cursor.execute("SELECT TOP 5 empID, firstName, lastName FROM OHEM")
        print("Muestra OHEM:", cursor.fetchall())
    except Exception as e:
        print(f"Error consultando OHEM: {e}")

    # Check OUSR
    try:
        cursor.execute("SELECT TOP 5 USERID, U_NAME FROM OUSR")
        print("Muestra OUSR:", cursor.fetchall())
    except Exception as e:
        print(f"Error consultando OUSR: {e}")

    print("\n--- 4. BUSCANDO 'U_NX_DIRECCION', etc. EN @FRMOBRAS (Obras/Proyectos) ---")
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '@FRMOBRAS' 
        AND (COLUMN_NAME LIKE 'U_nx_%' OR COLUMN_NAME LIKE 'U_NX_%')
        ORDER BY COLUMN_NAME
    """)
    columns = [row.COLUMN_NAME for row in cursor.fetchall()]
    print("Columnas U_NX_ en @FRMOBRAS:", columns)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"ERROR CRITICO: {e}")
