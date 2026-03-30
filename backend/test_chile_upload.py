import os
import django
import sys
import requests

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.documents.models import VisitReport

def test_upload():
    set_current_country('CL')
    sap_tx = SAPTransactionService()
    
    # Target report from today
    report = VisitReport.objects.get(id=20263) # RV-2026-072
    call_id = 26706 # Internal CallID
    
    print(f"Testing upload for Report {report.report_number}, CallID {call_id}")
    
    if not report.pdf_file:
        print("No PDF file in report.")
        return
        
    file_path = report.pdf_file.path
    filename = os.path.basename(file_path)
    
    print(f"File path: {file_path}")
    print(f"Filename: {filename}")
    
    # Manual trigger of upload to see result
    result = sap_tx.upload_attachment_to_service_call(call_id, file_path, filename)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_upload()
