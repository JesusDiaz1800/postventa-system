#!/usr/bin/env python
"""Test SAP Service Layer login (write connection)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
import django
django.setup()

from apps.sap_integration.sap_transaction_service import SAPTransactionService

s = SAPTransactionService()
print(f"URL: {s.base_url}")
print(f"DB: {s.company_db}")
print(f"User: {s.user}")

ok = s._login()
print(f"SL LOGIN: {'OK' if ok else 'FAILED'}")

if ok:
    print("Session cookies obtained successfully")
    s.logout()
    print("Logout OK")
else:
    print("ERROR: Could not authenticate with SAP Service Layer")
