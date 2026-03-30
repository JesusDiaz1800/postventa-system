"""Query technicians from SAP OHEM table"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'

import django
django.setup()

from django.db import connections

cursor = connections['sap_db_pe'].cursor()
cursor.execute("SELECT TOP 10 empID, firstName, lastName FROM OHEM ORDER BY empID")
rows = cursor.fetchall()
print("=== TECNICOS SAP PERU (TSTPOLPERU) ===")
for r in rows:
    print(f"  EmpID={r[0]}  Name={r[1]} {r[2]}")
