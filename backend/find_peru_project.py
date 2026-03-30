import os
import django
from django.db import connections

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

def find_project():
    with connections['sap_db_pe'].cursor() as cursor:
        cursor.execute("SELECT TOP 1 BPProjCode FROM OSCL WHERE Customer = 'CL20341778051' AND BPProjCode IS NOT NULL")
        row = cursor.fetchone()
        if row:
            print(f"Project for CL20341778051: {row[0]}")
        else:
            # If no project for this customer, look for ANY project in ORDR (Orders) or OPHRE
            cursor.execute("SELECT TOP 1 PrjCode FROM OPRJ WHERE Locked = 'N'")
            row = cursor.fetchone()
            if row:
                print(f"Random active project: {row[0]}")
            else:
                print("No project found in OPRJ")

if __name__ == "__main__":
    find_project()
