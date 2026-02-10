import os
import django
from django.db import connections

def analyze_incident_vs_visit():
    print("--- ANÁLISIS DIFERENCIAL: INCIDENCIA VS VISITA ---")
    try:
        if 'sap_db' not in connections:
            print("Error: 'sap_db' no configurada.")
            return

        conn = connections['sap_db']
        cursor = conn.cursor()
        
        # 1. Intentar descifrar los Nombres de los Tipos (problemTyp y callType)
        # Tablas probables: OSCP (Problem Types), OSCT (Call Types), OSCO (Origins?)
        print("\n1. Diccionario de Tipos (Intentando recuperar nombres):")
        try:
            cursor.execute("SELECT PrblmTypID, Name FROM OSCP")
            p_types = {row[0]: row[1] for row in cursor.fetchall()}
            print("  [Tipos de Problema encontrados]:")
            for pid, name in list(p_types.items())[:10]:
                print(f"    - ID {pid}: {name}")
                
            cursor.execute("SELECT CallTypeID, Name FROM OSCT")
            c_types = {row[0]: row[1] for row in cursor.fetchall()}
            print("  [Tipos de Llamada encontrados]:")
            for cid, name in list(c_types.items())[:10]:
                print(f"    - ID {cid}: {name}")
        except Exception as e:
            print(f"  (No se pudieron leer tablas auxiliares: {e})")

        # 2. Comparar el ID 167 (Visita rechazada) con potenciales Incidencias
        print("\n2. Comparativa:")
        
        # ID 167
        cursor.execute("SELECT callID, subject, problemTyp, callType FROM OSCL WHERE callID = 167")
        row_167 = cursor.fetchone()
        if row_167:
            p_name = p_types.get(row_167[2], 'Desconocido') if 'p_types' in locals() else row_167[2]
            c_name = c_types.get(row_167[3], 'Desconocido') if 'c_types' in locals() else row_167[3]
            print(f"  [RECHAZADO] ID 167: '{row_167[1]}' | Prob: {p_name} | Call: {c_name}")
        
        # Buscar "Reclamo" o "Falla" que NO sea "Visita"
        print("\n3. Buscando 'Reclamo' que NO tenga 'Visita' en el asunto:")
        query = """
        SELECT TOP 5 callID, subject, problemTyp, callType, descrption
        FROM OSCL 
        WHERE (subject LIKE '%Reclamo%' OR subject LIKE '%Falla%')
          AND subject NOT LIKE '%Visita%'
          AND subject NOT LIKE '%VT%'
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                p_name = p_types.get(r[2], 'Desconocido') if 'p_types' in locals() else r[2]
                print(f"  [CANDIDATO] ID {r[0]}: '{r[1]}' | Prob: {p_name}")
        else:
            print("  No se encontraron candidatos limpios de 'Visita'.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_incident_vs_visit()
