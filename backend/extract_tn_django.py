import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def extract_tn_django_default():
    # Usamos la conexión 'default' que ya sabemos que funciona con Windows Auth
    alias = 'default'
    try:
        print(f"Extracting TN using {alias} targeting TSTPOLPERU...")
        with connections[alias].cursor() as cursor:
            # Seleccionamos la base de datos de Perú
            cursor.execute("USE TSTPOLPERU")
            cursor.execute("EXEC sp_helptext 'SBO_SP_TransactionNotification'")
            lines = cursor.fetchall()
            
            full_text = "".join([l[0] for l in lines])
            
            # Buscar validación de Service Call (191)
            import re
            match = re.search(r"@object_type\s*=\s*'191'", full_text, re.IGNORECASE)
            if match:
                start = match.start()
                print("--- VALIDATION SECTION FOR 191 ---")
                print(full_text[start:start+2000])
            else:
                print("Section for 191 not found in TransactionNotification.")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_tn_django_default()
