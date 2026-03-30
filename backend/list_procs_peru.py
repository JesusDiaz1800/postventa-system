import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def list_procs():
    alias = 'default'
    try:
        print(f"Listing procedures in TSTPOLPERU using {alias}...")
        with connections[alias].cursor() as cursor:
            cursor.execute("USE TSTPOLPERU")
            cursor.execute("SELECT name FROM sys.procedures WHERE name LIKE '%Transaction%'")
            rows = cursor.fetchall()
            if not rows:
                print("No procedures found with 'Transaction' in name.")
            else:
                for row in rows:
                    print(f"Found Procedure: {row[0]}")
                    
            # Check if it was renamed to something else
            cursor.execute("SELECT name FROM sys.procedures WHERE name LIKE '%Notification%'")
            rows = cursor.fetchall()
            for row in rows:
                print(f"Found Procedure (Notification): {row[0]}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_procs()
