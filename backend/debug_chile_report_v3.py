import os
import django
import sys

# Setup Django - Assuming this script is in 'backend/'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.documents.models import VisitReport
from apps.audit.models import AuditLog
from django.db.models import Q

def check_chile():
    print("=== INVESTIGATING CHILE VISIT REPORT PDF ===")
    
    # 1. Get last report for Chile
    last_report = VisitReport.objects.filter(related_incident__country='CL').order_by('-created_at').first()
    
    if not last_report:
        print("No VisitReports found for Chile.")
        return

    print(f"Latest Report Found for Chile:")
    print(f" - ID: {last_report.id}")
    print(f" - Report Number: {last_report.report_number}")
    print(f" - Incident: {last_report.related_incident.code}")
    print(f" - Created at: {last_report.created_at}")
    print(f" - PDF file field: {last_report.pdf_file}")
    print(f" - PDF path field: {last_report.pdf_path}")
    print(f" - Sync Status: {last_report.sync_status}")
    print(f" - Last Synced At: {last_report.last_synced_at}")
    print(f" - Sync Error: {last_report.sync_error_message}")
    
    if last_report.pdf_file:
        try:
            full_path = last_report.pdf_file.path
            print(f" - PDF File full path: {full_path}")
            if os.path.exists(full_path):
                print(f" - PDF FILE EXISTS ON DISK. Size: {os.path.getsize(full_path)} bytes")
            else:
                print(f" - PDF FILE MISSING ON DISK!")
        except ValueError as e:
            print(f" - PDF file path error: {e}")
    else:
        print(" - PDF file field is EMPTY.")

    if last_report.pdf_path:
        print(f" - manual PDF path: {last_report.pdf_path}")
        if os.path.exists(last_report.pdf_path):
            print(f" - manual PDF FILE EXISTS ON DISK. Size: {os.path.getsize(last_report.pdf_path)} bytes")
        else:
            print(f" - manual PDF FILE MISSING ON DISK!")

    # 2. Check Audit Logs for this report
    print("\nRecent Audit Logs for this report or SAP errors:")
    logs = AuditLog.objects.filter(
        Q(description__icontains=last_report.report_number) | 
        Q(description__icontains=str(last_report.id))
    ).order_by('-created_at')[:20]
    
    for l in logs:
        print(f"[{l.created_at}] {l.action}: {l.description}")
        if l.details:
            print(f"   Details: {l.details}")

if __name__ == "__main__":
    check_chile()
