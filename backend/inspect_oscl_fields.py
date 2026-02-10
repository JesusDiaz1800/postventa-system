"""
Script para inspeccionar campos de la tabla OSCL de SAP
Verificar: city, commune, technician, ProblemTyp, contctCode, telephone
"""

import pyodbc

# Conexión a SAP
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
    
    print("=" * 80)
    print("INSPECCIÓN DE TABLA OSCL - CAMPOS REQUERIDOS")
    print("=" * 80)
    
    # Verificar estructura de la tabla primero
    print("\n1. COLUMNAS DE LA TABLA OSCL:")
    print("-" * 80)
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'OSCL'
        AND COLUMN_NAME IN (
            'City', 'U_NX_CIUDAD', 'U_Ciudad', 'city',
            'County', 'U_NX_COMUNA', 'U_Comuna', 'county',
            'technician', 'Technician', 'TechnicianCode', 'U_Technician',
            'ProblemTyp', 'U_ProblemTyp',
            'contctCode', 'contactCode', 'U_ContactCode',
            'telephone', 'Telephone', 'Tel', 'Phone'
        )
        ORDER BY COLUMN_NAME
    """)
    
    columns_found = []
    for row in cursor.fetchall():
        col_name, data_type, max_length = row
        columns_found.append(col_name)
        length_info = f"({max_length})" if max_length else ""
        print(f"  {col_name:<30} {data_type}{length_info}")
    
    if not columns_found:
        print("  ⚠️  Ninguna de las columnas esperadas fue encontrada")
        print("\n  Buscando columnas similares...")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'OSCL'
            AND (
                COLUMN_NAME LIKE '%city%' OR
                COLUMN_NAME LIKE '%ciudad%' OR
                COLUMN_NAME LIKE '%county%' OR
                COLUMN_NAME LIKE '%comuna%' OR
                COLUMN_NAME LIKE '%technic%' OR
                COLUMN_NAME LIKE '%problem%' OR
                COLUMN_NAME LIKE '%contact%' OR
                COLUMN_NAME LIKE '%phone%' OR
                COLUMN_NAME LIKE '%tel%'
            )
            ORDER BY COLUMN_NAME
        """)
        
        print("\n  Columnas similares encontradas:")
        for row in cursor.fetchall():
            print(f"    {row[0]:<30} {row[1]}")
    
    # Consultar datos de ejemplo
    print("\n2. DATOS DE EJEMPLO (últimos 3 registros):")
    print("-" * 80)
    
    # Construir query dinámicamente con las columnas encontradas
    query = """
        SELECT TOP 3
            callID,
            subject,
            customer,
            custmrName,
            itemCode,
            itemDescription,
            manufSN,
            internalSN,
            origin,
            priority,
            assignee,
            technician,
            ProblemTyp,
            contctCode,
            telephone,
            street,
            city,
            county,
            U_NX_CIUDAD,
            U_NX_COMUNA
        FROM OSCL
        WHERE callID IS NOT NULL
        ORDER BY callID DESC
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if rows:
            # Mostrar headers
            columns = [desc[0] for desc in cursor.description]
            print(f"\n  Columnas: {', '.join(columns)}\n")
            
            for i, row in enumerate(rows, 1):
                print(f"\n  Registro {i} (CallID: {row[0]}):")
                for col_name, value in zip(columns, row):
                    if value:
                        print(f"    {col_name:<20}: {value}")
        else:
            print("  No se encontraron registros")
            
    except Exception as e:
        print(f"  Error en query de ejemplo: {e}")
        print("\n  Intentando query simplificada...")
        
        cursor.execute("""
            SELECT TOP 3
                callID,
                subject,
                custmrName,
                technician,
                ProblemTyp,
                contctCode,
                telephone
            FROM OSCL
            WHERE callID IS NOT NULL
            ORDER BY callID DESC
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            print(f"\n  CallID: {row[0]}")
            print(f"    Subject: {row[1]}")
            print(f"    Customer: {row[2]}")
            print(f"    Technician: {row[3]}")
            print(f"    ProblemTyp: {row[4]}")
            print(f"    contctCode: {row[5]}")
            print(f"    telephone: {row[6]}")
    
    # Verificar tabla de contactos si existe
    print("\n3. VERIFICANDO TABLA OCPR (Contactos de Cliente):")
    print("-" * 80)
    
    try:
        cursor.execute("""
            SELECT TOP 3
                CntctCode,
                Name,
                Tel1,
                Tel2,
                Cellolar,
                CardCode
            FROM OCPR
            WHERE CntctCode IS NOT NULL
            ORDER BY CntctCode DESC
        """)
        
        rows = cursor.fetchall()
        if rows:
            print("  Estructura de OCPR encontrada:")
            for row in rows:
                print(f"    CntctCode: {row[0]}, Name: {row[1]}, Tel1: {row[2]}, Cellolar: {row[4]}")
        else:
            print("  Tabla OCPR existe pero está vacía")
            
    except Exception as e:
        print(f"  Tabla OCPR no encontrada o error: {e}")
    
    print("\n" + "=" * 80)
    print("INSPECCIÓN COMPLETADA")
    print("=" * 80)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    import traceback
    traceback.print_exc()
