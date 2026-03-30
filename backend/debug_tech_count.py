import sys, os
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.db import connections
from apps.core.thread_local import set_current_country

def count_techs():
    set_current_country('PE')
    db_alias = 'sap_db_pe'
    print(f"--- Contando Técnicos en {db_alias} con Filtro de Producción ---")
    query = """
        SELECT count(*)
        FROM OHEM 
        WHERE Active = 'Y' 
        AND (dept = 5 
             OR jobTitle LIKE '%Tecnico%' 
             OR jobTitle LIKE '%Tcnico%' 
             OR userId IS NOT NULL 
             OR salesPrson IS NOT NULL)
    """
    try:
        with connections[db_alias].cursor() as cursor:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"Total encontrados: {count}")
            
            # Listar nombres para ver quiénes son
            cursor.execute("""
                SELECT firstName, lastName, jobTitle, dept, userId, salesPrson 
                FROM OHEM 
                WHERE Active = 'Y' 
                AND (dept = 5 
                     OR jobTitle LIKE '%Tecnico%' 
                     OR jobTitle LIKE '%Tcnico%' 
                     OR userId IS NOT NULL 
                     OR salesPrson IS NOT NULL)
            """)
            rows = cursor.fetchall()
            for r in rows:
                print(f"- {r[0]} {r[1]} | Title: {r[2]} | Dept: {r[3]} | UserID: {r[4]} | Sales: {r[5]}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_techs()
