import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def extract_tn():
    alias = 'sap_db_pe'
    try:
        print(f"Extracting TransactionNotification from {alias}...")
        with connections[alias].cursor() as cursor:
            # Seleccionamos la definición de la SP
            cursor.execute("SELECT OBJECT_DEFINITION(OBJECT_ID('SBO_SP_TransactionNotification'))")
            row = cursor.fetchone()
            if row and row[0]:
                content = row[0]
                # Guardamos en un archivo para análisis
                with open('peru_tn_dump.sql', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("TransactionNotification extracted to peru_tn_dump.sql")
                
                # Buscamos la sección de Service Calls (191)
                idx = content.find("'191'")
                if idx != -1:
                    print("Found Service Call (191) validation section. Inspecting...")
                    section = content[idx:idx+2000]
                    print(section)
                else:
                    print("Service Call (191) section not found in short snippet.")
            else:
                print("Could not retrieve definition of SBO_SP_TransactionNotification")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_tn()
