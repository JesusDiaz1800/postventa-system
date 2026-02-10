import sys
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
from django.conf import settings
django.setup()

from apps.sap_integration.models import BusinessPartner, Project

def verify():
    print("Testing connection to SAP DB (TESTPOLIFUSION)...")
    try:
        # Try to count partners
        count = BusinessPartner.objects.count()
        print(f"✅ Connection Successful! Found {count} Business Partners.")
        
        # Try to fetch one
        bp = BusinessPartner.objects.using('sap_db').first()
        if bp:
            print(f"Sample Partner: {bp.card_code} - {bp.card_name}")
            
        return True
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return False

if __name__ == '__main__':
    verify()
