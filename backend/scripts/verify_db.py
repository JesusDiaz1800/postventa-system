import os
import sys
import django
from django.db import connections
from django.db.utils import OperationalError

# Add backend to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "postventa_system.settings")
django.setup()

def verify_connection():
    print("--- Verifying Default Database ---")
    db_conn = connections['default']
    try:
        c = db_conn.cursor()
        print("SUCCESS: Connected to default database.")
        c.execute("SELECT 1")
        print("SUCCESS: Executed simple query.")
    except OperationalError as e:
        print(f"FAILURE: OperationalError: {e}")
    except Exception as e:
        print(f"FAILURE: Error: {e}")

    print("\n--- Verifying SAP Database (if configured) ---")
    if 'sap_db' in connections:
         try:
            sap_conn = connections['sap_db']
            c_sap = sap_conn.cursor()
            print("SUCCESS: Connected to SAP database.")
         except Exception as e:
             print(f"WARNING: SAP database connection failed: {e}")
    else:
        print("INFO: SAP database not configured in settings.")

if __name__ == "__main__":
    verify_connection()
