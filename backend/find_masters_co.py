import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def find_master_tables():
    try:
        with connections['sap_db_co'].cursor() as cursor:
            # Buscar cualquier tabla que tenga que ver con "Type" o "Problem"
            cursor.execute("SELECT name FROM sys.tables WHERE name LIKE '%TYPE%' OR name LIKE '%PRB%' OR name LIKE '%PROB%'")
            tables = [r[0] for r in cursor.fetchall()]
            print(f"Tables found: {tables}")
            
            for t in tables:
                try:
                    cursor.execute(f"SELECT TOP 1 * FROM {t}")
                    print(f"Table {t} exists and has data.")
                except:
                    pass

            # Buscar especificamente OCTP y OTYP con comillas o diferentes esquemas
            for t in ['OCTP', 'OTYP', 'OSCO']:
                try:
                    cursor.execute(f"SELECT TOP 1 * FROM {t}")
                    print(f"Table {t} found!")
                except:
                    print(f"Table {t} NOT found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_master_tables()
