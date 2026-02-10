import os
import django
from django.db import connections

def comprehensive_sap_analysis():
    """Análisis exhaustivo de OSCL para encontrar TODAS las incidencias potenciales"""
    print("=" * 60)
    print("ANÁLISIS EXHAUSTIVO DE SAP OSCL")
    print("=" * 60)
    
    try:
        if 'sap_db' not in connections:
            print("Error: 'sap_db' no configurada.")
            return

        conn = connections['sap_db']
        cursor = conn.cursor()
        
        # 1. Total de registros
        cursor.execute("SELECT COUNT(*) FROM OSCL")
        total = cursor.fetchone()[0]
        print(f"\n1. TOTAL DE REGISTROS: {total}")
        
        # 2. Distribución por callType
        print("\n2. DISTRIBUCIÓN POR TIPO DE LLAMADA (callType):")
        cursor.execute("""
            SELECT o.callType, t.Name, COUNT(*) as cnt
            FROM OSCL o
            LEFT JOIN OSCT t ON o.callType = t.CallTypeID
            GROUP BY o.callType, t.Name
            ORDER BY cnt DESC
        """)
        for row in cursor.fetchall():
            print(f"   callType={row[0]} ({row[1]}): {row[2]} registros")
        
        # 3. Distribución por problemTyp (top 15)
        print("\n3. DISTRIBUCIÓN POR TIPO DE PROBLEMA (problemTyp) - Top 15:")
        cursor.execute("""
            SELECT TOP 15 o.problemTyp, p.Name, COUNT(*) as cnt
            FROM OSCL o
            LEFT JOIN OSCP p ON o.problemTyp = p.PrblmTypID
            GROUP BY o.problemTyp, p.Name
            ORDER BY cnt DESC
        """)
        for row in cursor.fetchall():
            print(f"   problemTyp={row[0]} ({row[1]}): {row[2]} registros")
        
        # 4. Búsqueda por palabras clave en TODOS los campos de texto
        keywords = [
            'RECLAMO', 'GARANTIA', 'LABORATORIO', 'RUPTURA', 'FUGA', 
            'FALLA', 'DEFECTO', 'ROTURA', 'QUIEBRE', 'FILTRACION',
            'POST VENTA', 'POSTVENTA', 'REPARACION', 'DEVOLUCION'
        ]
        
        print("\n4. BÚSQUEDA POR PALABRAS CLAVE (en subject + descrption):")
        total_keyword_matches = 0
        for kw in keywords:
            query = f"""
            SELECT COUNT(*) FROM OSCL 
            WHERE subject LIKE '%{kw}%' 
               OR descrption LIKE '%{kw}%'
               OR U_NX_OBS_MATRIZ LIKE '%{kw}%'
               OR U_NX_OBS_MURO LIKE '%{kw}%'
            """
            cursor.execute(query)
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"   '{kw}': {count} registros")
                total_keyword_matches += count
        
        # 5. Conteo de registros únicos con cualquier palabra clave
        all_like = " OR ".join([f"(subject LIKE '%{kw}%' OR descrption LIKE '%{kw}%' OR U_NX_OBS_MATRIZ LIKE '%{kw}%' OR U_NX_OBS_MURO LIKE '%{kw}%')" for kw in keywords])
        query = f"SELECT COUNT(*) FROM OSCL WHERE {all_like}"
        cursor.execute(query)
        unique_keyword_count = cursor.fetchone()[0]
        print(f"\n   TOTAL ÚNICOS con palabras clave: {unique_keyword_count}")
        
        # 6. Combinación: callType=1 OR palabras clave
        combined_query = f"""
        SELECT COUNT(*) FROM OSCL 
        WHERE callType = 1 
           OR ({all_like})
        """
        cursor.execute(combined_query)
        combined_count = cursor.fetchone()[0]
        print(f"\n5. TOTAL COMBINADO (callType=1 + Palabras Clave): {combined_count}")
        
        # 7. Muestra de 10 registros que cumplen criterios
        print("\n6. MUESTRA DE 10 REGISTROS QUE CUMPLEN CRITERIOS:")
        sample_query = f"""
        SELECT TOP 10 callID, callType, problemTyp, subject, createDate
        FROM OSCL 
        WHERE callType = 1 
           OR ({all_like})
        ORDER BY createDate DESC
        """
        cursor.execute(sample_query)
        for row in cursor.fetchall():
            subject_short = (row[3][:50] + '...') if row[3] and len(row[3]) > 50 else row[3]
            print(f"   ID:{row[0]} | Type:{row[1]} | Prob:{row[2]} | {subject_short}")
        
        print("\n" + "=" * 60)
        print("FIN DEL ANÁLISIS")
        print("=" * 60)

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_sap_analysis()
