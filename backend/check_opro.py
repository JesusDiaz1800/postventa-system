import os
import django
from django.db import connections

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_opro():
    db_alias = 'sap_db_pe'
    print(f"--- Tipos de Problema en OPRO ({connections[db_alias].settings_dict['NAME']}) ---")
    try:
        with connections[db_alias].cursor() as cursor:
            cursor.execute("SELECT AbsEntry, Name FROM OPRO")
            for row in cursor.fetchall():
                print(f"ID (AbsEntry): {row[0]}, Name: {row[1]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_opro()
