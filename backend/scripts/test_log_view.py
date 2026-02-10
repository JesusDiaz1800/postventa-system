
import os
import sys
import django
# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.documents.views_traceability import send_supplier_report_email
from apps.documents.models import SupplierReport

def test_view_logic():
    print("--- TESTING LOG-ONLY VIEW ---")
    
    # 1. Get Report 4 (or any)
    try:
        report = SupplierReport.objects.get(pk=4)
        print(f"Target Report: {report} (PK: 4)")
    except SupplierReport.DoesNotExist:
        print("Report 4 not found, using first available.")
        report = SupplierReport.objects.first()
        if not report:
            print("No reports found.")
            return

    # 2. Mock Request
    factory = APIRequestFactory()
    url = f'/api/documents/supplier-reports/{report.pk}/send-email/'
    data = {
        'to': 'test@example.com',
        'action': 'log_only'
    }
    request = factory.post(url, data, format='json')
    
    # 3. Authenticate
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True).first()
    force_authenticate(request, user=admin)
    
    # 4. Execute
    try:
        response = send_supplier_report_email(request, pk=report.pk)
        print(f"\nResponse Code: {response.status_code}")
        print(f"Response Data: {response.data}")
    except Exception as e:
        import traceback
        print(f"\n[CRITICAL FAILURE] {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_view_logic()
