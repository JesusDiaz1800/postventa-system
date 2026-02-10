import os
from django.db import connections

def analyze_oscl():
    print("--- Análisis de Tabla OSCL (SAP) ---")
    try:
        if 'sap_db' not in connections:
            print("Error: 'sap_db' no está configurada en settings.")
            return

        conn = connections['sap_db']
        cursor = conn.cursor()
        
        # 1. Contar registros totales
        cursor.execute("SELECT COUNT(*) FROM OSCL")
        total_count = cursor.fetchone()[0]
        print(f"Total de registros en OSCL: {total_count}")
        
        # 2. Obtener columnas
        cursor.execute("SELECT TOP 1 * FROM OSCL")
        columns = [col[0] for col in cursor.description]
        print(f"\nColumnas detectadas ({len(columns)}):")
        
        # Buscar campos de texto candidatos
        text_candidates = [c for c in columns if any(x in c.lower() for x in ['desc', 'rem', 'comm', 'note', 'obs', 'det', 'text'])]
        print(f"Campos de texto candidatos: {text_candidates}")

        print("\n--- Muestra de Contenido de Texto ---")
        # Mostrar muestra de estos campos para ver cuál tiene la info real
        fields_to_check = ['subject'] + text_candidates[:5] # Check subject + up to 5 others to avoid massive query
        
        query_cols = ", ".join(fields_to_check)
        try:
            cursor.execute(f"SELECT TOP 5 {query_cols} FROM OSCL WHERE descrption IS NOT NULL OR subject IS NOT NULL")
            rows = cursor.fetchall()
            for row in rows:
                print(f"\nRegistro:")
                for i, field in enumerate(fields_to_check):
                    val = row[i]
                    if val and len(str(val)) > 50: val = str(val)[:50] + "..."
                    print(f"  - {field}: {val}")
        except Exception as e:
            print(f"Error consultando textos: {e}")
        
        # 4. Verificar contenido de campos de usuario (UDF) para ID conocido
        print("\n--- INVESTIGACIÓN DE CAMPOS DE USUARIO (ID 167) ---")
        
        # Lista de campos U_NX detectados previamente
        udfs = ['U_NX_OBS_MURO', 'U_NX_OBS_MATRIZ', 'U_NX_OBS_LOSA', 'U_NX_OBS_ALMAC', 'U_NX_OBS_PRE_ARM', 'U_NX_OBS_EXTER', 'descrption']
        cols_query = ", ".join(udfs)
        
        query = f"SELECT {cols_query} FROM OSCL WHERE callID = 167"
        
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            print(f"Datos para ID 167:")
            for i, field in enumerate(udfs):
                content = row[i]
                if content:
                    print(f"  [{field}]: {str(content)[:100]}...") # Mostrar primeros 100 caracteres
                else:
                    print(f"  [{field}]: (vacío)")
        else:
            print("No se encontró el ID 167.")

    except Exception as e:
        print(f"Error fatal durante análisis: {e}")

if __name__ == "__main__":
    analyze_oscl()
