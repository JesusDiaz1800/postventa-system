import os
import django
from django.db import connections

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_prod_pe():
    # Intentar usar el alias que apunta a la DB de producción de PE
    db_alias = 'sap_db_pe'
    print(f"--- Consultando DB: {connections[db_alias].settings_dict['NAME']} ---")
    try:
        with connections[db_alias].cursor() as cursor:
            # Listar posiciones
            cursor.execute("SELECT posID, name FROM OHPS")
            positions = {row[0]: row[1] for row in cursor.fetchall()}
            print(f"Posiciones: {positions}")
            
            # Contar empleados por posición
            cursor.execute("""
                SELECT position, COUNT(*) 
                FROM OHEM 
                WHERE Active = 'Y' 
                GROUP BY position
            """)
            print("\nEmpleados Activos por Posición:")
            for row in cursor.fetchall():
                pos_name = positions.get(row[0], "Desconocida")
                print(f"Pos {row[0]} ({pos_name}): {row[1]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_prod_pe()
