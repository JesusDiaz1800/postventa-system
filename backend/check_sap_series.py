import os
import django
from django.db import connections

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_series():
    db_alias = 'sap_db_pe'
    print(f"--- NNM1 (Series) en: {connections[db_alias].settings_dict['NAME']} ---")
    try:
        with connections[db_alias].cursor() as cursor:
            cursor.execute("SELECT TOP 1 * FROM NNM1 WHERE ObjectCode = '191'")
            cols = [column[0] for column in cursor.description]
            print(f"Columnas: {cols}")
            
            cursor.execute("SELECT * FROM NNM1 WHERE ObjectCode = '191'")
            for row in cursor.fetchall():
                print(row)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_series()
