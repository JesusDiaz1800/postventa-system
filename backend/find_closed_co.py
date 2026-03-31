import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
django.setup()

from django.db import connections

def find_closed_calls():
    try:
        print("=== LLAMADAS NO ABIERTAS EN CO ===")
        with connections['sap_db_co'].cursor() as cursor:
            cursor.execute("SELECT TOP 10 callID, DocNum, Status, Subject FROM OSCL WHERE Status != -3")
            rows = cursor.fetchall()
            for r in rows:
                print(f"  CallID: {r[0]}, DocNum: {r[1]}, Status: {r[2]}, Subject: {r[3]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_closed_calls()
