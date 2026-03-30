import os
import django
from django.db import connections

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check_sap_config():
    db_alias = 'sap_db_pe'
    print(f"--- Investigando Configuracion en: {connections[db_alias].settings_dict['NAME']} ---")
    try:
        with connections[db_alias].cursor() as cursor:
            tables = [
                ('OPRO', 'Tipo de Problema'),
                ('OSCT', 'Tipo de Llamada'),
                ('OSCO', 'Origen de Llamada')
            ]
            for table, label in tables:
                print(f"\n--- {label} ({table}) ---")
                try:
                    cursor.execute(f"SELECT TOP 1 * FROM {table}")
                    cols = [column[0] for column in cursor.description]
                    print(f"Columnas: {cols}")
                    
                    id_col = cols[0]
                    name_col = cols[1] if len(cols) > 1 else cols[0]
                    
                    cursor.execute(f"SELECT {id_col}, {name_col} FROM {table}")
                    for row in cursor.fetchall():
                        print(f"ID: {row[0]}, Name: {row[1]}")
                except Exception as e:
                    print(f"Error en {table}: {e}")
                    
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    check_sap_config()
