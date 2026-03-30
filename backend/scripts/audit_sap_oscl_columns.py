import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
import django; django.setup()
from django.db import connections

print("=== OSCL COLUMNS ===")
with connections['sap_db'].cursor() as c:
    c.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='OSCL' ORDER BY ORDINAL_POSITION")
    for r in c.fetchall():
        print(f"  {r[0]:35s} {r[1]}")

print("\n=== SAMPLE: Call 26480 ===")
with connections['sap_db'].cursor() as c:
    c.execute("""SELECT callID, subject, customer, custmrName, status, createDate, createTime,
        closeDate, technician, descrption, BPShipAddr, BPProjCode, U_NX_NOM_PRO,
        U_NX_VENDEDOR, problemTyp, priority, origin, Telephone, contctCode, 
        assignee, SalesPersonCode FROM OSCL WHERE callID=26480""")
    row = c.fetchone()
    cols = [d[0] for d in c.description]
    if row:
        for col, val in zip(cols, row):
            print(f"  {col:25s} = {val}")
