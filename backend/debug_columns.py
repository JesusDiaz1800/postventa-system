import sys, os
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.db import connections
from apps.core.thread_local import set_current_country

def debug():
    set_current_country('PE')
    db_alias = 'sap_db_pe'
    print(f"--- Inspeccionando Columnas OHEM en {db_alias} ---")
    try:
        with connections[db_alias].cursor() as cursor:
            cursor.execute("SELECT TOP 1 * FROM OHEM")
            columns = [col[0] for col in cursor.description]
            print(f"Columnas encontradas ({len(columns)}):")
            print(columns)
            
            # Buscar variaciones de 'email'
            email_cols = [c for c in columns if 'EMAIL' in c.upper()]
            print(f"Columnas relacionadas con EMail: {email_cols}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug()
