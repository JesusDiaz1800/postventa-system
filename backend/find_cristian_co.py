import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def find_cristian_co():
    alias = 'sap_db_co'
    try:
        print(f"Searching for 'Cristian' or 'Peña' in {alias} (OHEM)...")
        with connections[alias].cursor() as cursor:
            # Búsqueda amplia
            query = """
            SELECT empID, firstName, lastName, middleName, userId, Active 
            FROM OHEM 
            WHERE firstName LIKE '%Cristian%' 
               OR lastName LIKE '%Peña%' 
               OR lastName LIKE '%Pena%' 
               OR middleName LIKE '%Cristian%'
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if not rows:
                print("No se encontró a nadie con ese nombre en Colombia.")
                # Listar los primeros 10 activos para ver si hay algún técnico
                cursor.execute("SELECT TOP 10 empID, firstName, lastName FROM OHEM WHERE Active = 'Y'")
                print("\nPrimeros 10 empleados activos en Colombia:")
                for r in cursor.fetchall():
                    print(r)
            else:
                for row in rows:
                    print(f"ID: {row[0]}, Nombre: {row[1]} {row[3] or ''} {row[2]}, UserID: {row[4]}, Activo: {row[5]}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_cristian_co()
