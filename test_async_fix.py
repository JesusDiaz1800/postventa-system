
import os
import django
import sys
import time

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.documents.models import VisitReport
from apps.documents.services.report_sync_service import ReportSyncService

def test_async():
    set_current_country('CL')
    report_id = 20269 # RV-2026-076
    try:
        report = VisitReport.objects.get(id=report_id)
        print(f"Triggering ASYNC sync for report {report.report_number}...")
        
        # Call the async method
        # Signature: sync_report_async(report_id, attachments_ids=None, img_descriptions=None, has_manual_pdf=False, user=None)
        ReportSyncService.sync_report_async(report_id)
        
        print("Waiting 10 seconds for the thread to complete...")
        time.sleep(10)
        
        report.refresh_from_db()
        print(f"Final PDF: {report.pdf_file.name if report.pdf_file else 'None'}")
        print(f"Final Sync Status: {report.sync_status}")
        
        if report.pdf_file and os.path.exists(report.pdf_file.path):
            print("SUCCESS: Asynchronous PDF generation verified.")
        else:
            print("FAILED: PDF not found after waiting.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_async()
