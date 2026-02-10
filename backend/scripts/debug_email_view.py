
import os
import sys
import django
# Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.documents.views_traceability import send_supplier_report_email
from apps.documents.models import SupplierReport

def debug_view():
    print("--- DEBUG EMAIL VIEW ---")
    
    # 1. Get Report
    try:
        report = SupplierReport.objects.get(pk=4)
        print(f"Found Report: {report} (PK: 4)")
    except SupplierReport.DoesNotExist:
        print("Report 4 not found. Finding first available report...")
        report = SupplierReport.objects.first()
        if not report:
            print("No SupplierReport found! Cannot reproduce.")
            return
        print(f"Using Report: {report} (PK: {report.pk})")

    # 2. Setup Request
    factory = APIRequestFactory()
    url = f'/api/documents/supplier-reports/{report.pk}/send-email/'
    data = {
        'to': 'test@example.com',
        'subject': 'Debug Subject',
        'message': 'Debug Message'
    }
    request = factory.post(url, data, format='json')
    
    # Authenticate
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("No admin user found to authenticate.")
        return
    force_authenticate(request, user=admin_user)
    
    # 3. Call View
    print("\nCalling view...")
    try:
        response = send_supplier_report_email(request, pk=report.pk)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Data: {response.data}")
    except Exception as e:
        import traceback
        print(f"\n[CRITICAL] View raised unhandled exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_view()
