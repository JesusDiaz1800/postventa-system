import os
import django
import sys

# Configurar entorno Django
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from django.db import connections
from django.db.utils import OperationalError

def test_connection(alias):
    print(f"--- Probando conexión: {alias} ---")
    try:
        connection = connections[alias]
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            print(f"STATUS: EXITOSO (Resultado: {row[0]})")
            
            # Probar tabla OCRD (Clientes)
            try:
                cursor.execute("SELECT TOP 1 CardCode, CardName FROM OCRD")
                customer = cursor.fetchone()
                if customer:
                    print(f"TABLA OCRD: ACCESIBLE (Cliente: {customer[0]} - {customer[1]})")
                else:
                    print("TABLA OCRD: ACCESIBLE pero VACÍA")
            except Exception as e:
                print(f"TABLA OCRD: ERROR - {e}")
                
    except OperationalError as e:
        print(f"STATUS: FALLO DE CONEXIÓN - {e}")
    except Exception as e:
        print(f"STATUS: ERROR INESPERADO - {e}")
    print("\n")

if __name__ == "__main__":
    db_aliases = ['sap_db', 'sap_db_pe', 'sap_db_co']
    for alias in db_aliases:
        test_connection(alias)
