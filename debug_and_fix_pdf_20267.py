
import os
import django
import sys
import io

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.documents.models import VisitReport
from apps.documents.services.report_sync_service import ReportSyncService

def verify():
    set_current_country('CL')
    report_id = 20267
    try:
        report = VisitReport.objects.get(id=report_id)
        print(f"Starting force sync for report {report.report_number} (ID: {report_id})")
        print(f"Initial PDF: {report.pdf_file.name if report.pdf_file else 'None'}")
        
        # Trigger sync process
        # _sync_process(report_id, attachments_ids, img_descriptions, has_manual_pdf, user_id)
        ReportSyncService._sync_process(report_id, [], [], False, None)
        
        # Refresh and check
        report.refresh_from_db()
        print(f"Final PDF: {report.pdf_file.name if report.pdf_file else 'None'}")
        print(f"Final Sync Status: {report.sync_status}")
        
        if report.pdf_file:
            full_path = report.pdf_file.path
            print(f"PDF exists at: {full_path}")
            if os.path.exists(full_path):
                print("SUCCESS: File physically exists on disk.")
            else:
                print("FAILED: DB record exists but file NOT found on disk.")
        else:
            print("FAILED: PDF was not generated.")
            
    except Exception as e:
        print(f"ERROR during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
