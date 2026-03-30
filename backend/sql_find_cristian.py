import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def find_cristian():
    alias = 'sap_db_co'
    try:
        print(f"Connecting to {alias}...")
        with connections[alias].cursor() as cursor:
            # Seleccionamos campos básicos y el rol
            cursor.execute("SELECT EmpID, firstName, lastName, JobTitle, Role FROM OHEM WHERE firstName LIKE %s OR lastName LIKE %s", ['%Cristian%', '%Peña%'])
            rows = cursor.fetchall()
            
            if not rows:
                print("No se encontró a Cristian Peña")
            else:
                for row in rows:
                    print(f"ID: {row[0]}, Nombre: {row[1]} {row[2]}, Cargo: {row[3]}, Role: {row[4]}")
                    
    except Exception as e:
        print(f"Error consultando SQL: {str(e)}")

if __name__ == "__main__":
    find_cristian()
