import os
import sys
import django

# Add the backend directory to sys.path
backend_dir = r"c:\Users\jdiaz\Desktop\postventa-system\backend"
sys.path.append(backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country, get_current_country
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from django.conf import settings

def check_context():
    set_current_country('PE')
    country = get_current_country()
    print(f"Current Country: {repr(country)}")
    print(f"Is country PE? {country == 'PE'}")
    
    print(f"Settings.SAP_SL_SERIES_PE: {settings.SAP_SL_SERIES_PE}")
    
    sap_tx = SAPTransactionService()
    print(f"SAP TX Series: {sap_tx.series}")
    print(f"SAP TX DB: {sap_tx.company_db}")

if __name__ == "__main__":
    check_context()
