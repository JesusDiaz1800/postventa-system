import os
import django
from django.db import connections

def inspect_template_records():
    print("--- INVESTIGACIÓN DE PLANTILLA ESTÁNDAR ---")
    try:
        if 'sap_db' not in connections:
            return

        conn = connections['sap_db']
        cursor = conn.cursor()
        
        # Traer un registro completo que contenga 'RECLAMO'
        query = """
        SELECT TOP 1 callID, subject, descrption, U_NX_OBS_MATRIZ, U_NX_OBS_MURO, problemTyp, callType
        FROM OSCL 
        WHERE subject LIKE '%RECLAMO%' AND subject LIKE '%GARANTIA%'
        """
        
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            print(f"\n** REGISTRO EJEMPLO (ID {row[0]}) **")
            print(f"ASUNTO COMPLETO:\n{row[1]}\n")
            print(f"DESCRIPCIÓN: {row[2]}")
            print(f"U_NX_OBS_MATRIZ: {row[3]}")
            print(f"U_NX_OBS_MURO: {row[4]}")
            print(f"problemTyp: {row[5]}, callType: {row[6]}")
            
            # Ahora contemos cuántos usan callType=1 (Post-Vent real)
            print("\n\n--- FILTRANDO SOLO POR CRITERIOS ESTRICTOS ---")
            strict_query = """
            SELECT COUNT(*) FROM OSCL 
            WHERE callType = 1 
               OR problemTyp IN (33, 16)
            """
            cursor.execute(strict_query)
            strict_count = cursor.fetchone()[0]
            print(f"SOLO callType=1 o problemTyp=33/16 (Post-Venta/Filtración): {strict_count} registros")
            
            # Verificar si esos ~1900 tienen observaciones reales
            print("\n--- ¿LOS ~1900 TIENEN CONTENIDO REAL? ---")
            cursor.execute("""
            SELECT COUNT(*) FROM OSCL 
            WHERE subject LIKE '%RECLAMO%' 
              AND (U_NX_OBS_MATRIZ IS NOT NULL AND LEN(U_NX_OBS_MATRIZ) > 10)
            """)
            with_content = cursor.fetchone()[0]
            print(f"Registros con palabras clave Y contenido en UDF: {with_content}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_template_records()
