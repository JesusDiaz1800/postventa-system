import os
import django
from django.db import connections

def analyze_candidates_breakdown():
    print("--- DESGLOSE DE CANDIDATOS (PARA REDUCIR EL VOLUMEN) ---")
    try:
        if 'sap_db' not in connections:
            print("Error: 'sap_db' no configurada.")
            return

        conn = connections['sap_db']
        cursor = conn.cursor()
        
        # 1. Total con filtros actuales
        keywords = [
            'RECLAMO', 'GARANTIA', 'LABORATORIO', 'RUPTURA', 'FUGA', 
            'FALLA', 'DEFECTO', 'ROTURA', 'QUIEBRE', 'FILTRACION',
            'POST VENTA'
        ]
        
        kw_filter = " OR ".join([f"subject LIKE '%{kw}%' OR descrption LIKE '%{kw}%' OR U_NX_OBS_MATRIZ LIKE '%{kw}%'" for kw in keywords])
        # Tipos estrictos
        pt_filter = "33, 16, 25, 26, 3" 
        
        query_base = f"""
        FROM OSCL 
        WHERE 
           callType = 1
           OR problemTyp IN ({pt_filter})
           OR ({kw_filter})
        """
        
        # 2. Desglose por Palabra Clave (aprox)
        print("\n=== ¿DE DÓNDE VIENEN LOS 2200 REGISTROS? ===")
        for kw in keywords:
            cursor.execute(f"SELECT COUNT(*) {query_base} AND (subject LIKE '%{kw}%')")
            cnt = cursor.fetchone()[0]
            if cnt > 0:
                print(f" - Palabra '{kw}': {cnt} registros")
                # Mostrar 3 ejemplos de asuntos
                cursor.execute(f"SELECT TOP 3 subject {query_base} AND (subject LIKE '%{kw}%')")
                for r in cursor.fetchall():
                    print(f"     Ej: {r[0][:60]}...")

        # 3. Desglose por Tipo de Problema
        print("\n=== DESGLOSE POR TIPO (Incidencias Codificadas) ===")
        cursor.execute(f"""
        SELECT problemTyp, COUNT(*) 
        {query_base} 
        GROUP BY problemTyp 
        ORDER BY COUNT(*) DESC
        """)
        for row in cursor.fetchall():
            print(f" - Tipo {row[0]}: {row[1]} registros")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_candidates_breakdown()
