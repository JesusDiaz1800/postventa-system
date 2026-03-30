import os
import django
import sys

# Setup Django - Assuming this script is in 'backend/'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country, get_current_country
from apps.documents.models import VisitReport
from apps.audit.models import AuditLog
from django.db.models import Q

def check_chile():
    print(f"=== INVESTIGATING CHILE VISIT REPORT PDF ===")
    set_current_country('CL')
    print(f"Current Country Context: {get_current_country()}")
    
    # 1. Get last report for Chile
    # In 'default' DB, all reports should theoretically be Chile if isolation is working
    last_report = VisitReport.objects.all().order_by('-created_at').first()
    
    if not last_report:
        print("No VisitReports found in 'default' (Chile) database.")
        return

    print(f"Latest Report Found:")
    print(f" - ID: {last_report.id}")
    print(f" - Report Number: {last_report.report_number}")
    print(f" - Incident Code: {last_report.related_incident.code if last_report.related_incident else 'N/A'}")
    print(f" - Created at: {last_report.created_at}")
    print(f" - PDF file field: {last_report.pdf_file}")
    print(f" - PDF path field: {last_report.pdf_path}")
    print(f" - Sync Status: {last_report.sync_status}")
    
    if last_report.pdf_file:
        try:
            full_path = last_report.pdf_file.path
            print(f" - PDF File path: {full_path}")
            if os.path.exists(full_path):
                print(f" - PDF FILE EXISTS ON DISK. Size: {os.path.getsize(full_path)} bytes")
            else:
                print(f" - PDF FILE MISSING ON DISK!")
        except Exception as e:
            print(f" - Error accessing pdf_file.path: {e}")
    else:
        print(" - PDF file field is EMPTY.")

    if last_report.pdf_path:
        print(f" - manual PDF path: {last_report.pdf_path}")
        if os.path.exists(last_report.pdf_path):
            print(f" - manual PDF FILE EXISTS ON DISK. Size: {os.path.getsize(last_report.pdf_path)} bytes")
        else:
            print(f" - manual PDF FILE MISSING ON DISK!")

    # 2. Check Audit Logs
    print("\nRecent Audit Logs related to this report:")
    relevant_logs = AuditLog.objects.filter(
        Q(description__icontains=last_report.report_number) |
        Q(description__icontains=str(last_report.id)) |
        Q(action='sap_sync_error')
    ).order_by('-created_at')[:15]
    
    for l in relevant_logs:
        print(f"[{l.created_at}] {l.action}: {l.description}")
        if l.details:
            print(f"   Details: {l.details}")

if __name__ == "__main__":
    check_chile()
