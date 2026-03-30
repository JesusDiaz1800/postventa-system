import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def find_cl_data():
    alias = 'sap_db' # Chile SAP
    try:
        with connections[alias].cursor() as cursor:
            # 1. Valid customer
            cursor.execute("SELECT TOP 1 CardCode, CardName FROM OCRD WHERE CardType = 'C' AND validFor = 'Y'")
            row = cursor.fetchone()
            if row:
                print(f"Chile Customer: {row[0]} ({row[1]})")
            
            # 2. Valid Project
            cursor.execute("SELECT TOP 1 PrjCode FROM OPRJ WHERE Locked = 'N'")
            row = cursor.fetchone()
            if row:
                print(f"Chile Project: {row[0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_cl_data()
