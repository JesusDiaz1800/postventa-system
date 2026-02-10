import os
import django
from django.db import connections

def test_sap_import():
    print("--- SIMULACIÓN DE IMPORTACIÓN SAP (DRY RUN) ---")
    try:
        if 'sap_db' not in connections:
            print("Error: 'sap_db' no está configurada.")
            return

        conn = connections['sap_db']
        cursor = conn.cursor()
        
        # 1. Definir consulta con filtros de palabras clave
        # Incluimos los campos UDF clave
        keywords = ['POST VENTA', 'RECLAMO', 'RECLAM', 'GARANTIA', 'FALLA', 'ROTURA', 'FUGA', 'DEFECTO', 'REPARACION']
        like_clauses = " OR ".join([f"subject LIKE '%{kw}%'" for kw in keywords])
        
        # Consultamos ID 167 explícitamente + 5 ejemplos aleatorios recientes
        query = f"""
        SELECT TOP 5 callID, customer, custmrName, subject, createDate, status, 
               U_NX_OBS_MATRIZ, U_NX_OBS_MURO, descrption
        FROM OSCL 
        WHERE ({like_clauses})
        ORDER BY createDate DESC
        """
        
        print(f"Ejecutando consulta de muestra...")
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # También traemos el 167 si no salió en el TOP 5
        cursor.execute(f"""
        SELECT callID, customer, custmrName, subject, createDate, status, 
               U_NX_OBS_MATRIZ, U_NX_OBS_MURO, descrption
        FROM OSCL 
        WHERE callID = 167
        """)
        row_167 = cursor.fetchone()
        
        # Combinar resultados (sin duplicar si 167 ya estaba)
        all_rows = rows
        if row_167 and not any(r[0] == 167 for r in rows):
            all_rows = [row_167] + rows # Poner al principio

        print(f"\nSe encontraron {len(all_rows)} registros de muestra para revisar:\n")
        
        for row in all_rows:
            call_id = row[0]
            customer_code = row[1]
            customer_name = row[2]
            subject = row[3]
            create_date = row[4]
            status = row[5]
            
            # Lógica de Descripción Combinada
            obs_matriz = row[6]
            obs_muro = row[7]
            std_desc = row[8]
            
            final_description = ""
            if obs_matriz:
                final_description += f"[Obs. Matriz]: {obs_matriz}\n"
            if obs_muro:
                final_description += f"[Obs. Muro]: {obs_muro}\n"
            if std_desc:
                final_description += f"[Desc. Std]: {std_desc}"
            
            if not final_description.strip():
                final_description = "(Sin descripción detallada disponible)"

            print(f"--- INCIDENCIA SIMULADA: {call_id} ---")
            print(f"Cliente: {customer_name} ({customer_code})")
            print(f"Fecha: {create_date}")
            print(f"Asunto (Referencia): {subject}")
            print(f"Descripción Extraída:\n{final_description}")
            print("-" * 50)

    except Exception as e:
        print(f"Error durante simulación: {e}")

if __name__ == "__main__":
    test_sap_import()
