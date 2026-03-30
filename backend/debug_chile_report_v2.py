import os
import django
import sys

# Setup Django - Assuming this script is in 'backend/'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.reports.models import VisitReport
from apps.audit.models import AuditLog
from django.db.models import Q

def check_chile():
    print("=== INVESTIGATING CHILE VISIT REPORT PDF ===")
    
    # 1. Get last report for Chile
    # We use incident__country='CL' because VisitReport doesn't have country field directly usually
    last_report = VisitReport.objects.filter(incident__country='CL').order_by('-created_at').first()
    
    if not last_report:
        # Try without country filter just to see what's the last report overall
        last_any = VisitReport.objects.all().order_by('-created_at').first()
        if last_any:
            print(f"No Chile report found, but last overall was ID {last_any.id} for {last_any.incident.country}")
        else:
            print("No VisitReports found at all.")
        return

    print(f"Latest Report Found for Chile:")
    print(f" - ID: {last_report.id}")
    print(f" - Incident: {last_report.incident.code}")
    print(f" - Created at: {last_report.created_at}")
    print(f" - PDF file field: {last_report.pdf_file}")
    print(f" - SAP DocNum/ID: {last_report.sap_doc_entry} / {last_report.sap_doc_num}")
    
    if last_report.pdf_file:
        full_path = last_report.pdf_file.path
        print(f" - Full path: {full_path}")
        if os.path.exists(full_path):
            print(f" - FILE EXISTS ON DISK. Size: {os.path.getsize(full_path)} bytes")
        else:
            print(f" - FILE MISSING ON DISK!")
    else:
        print(" - PDF file field is EMPTY.")

    # 2. Check Audit Logs for this report
    print("\nRecent Audit Logs for this report (ID: {last_report.id}) or SAP errors:")
    logs = AuditLog.objects.filter(
        Q(description__icontains=str(last_report.id)) | 
        Q(action__icontains='sap_sync_error')
    ).order_by('-created_at')[:20]
    
    for l in logs:
        print(f"[{l.created_at}] {l.action}: {l.description}")
        if l.details:
            print(f"   Details: {l.details}")

if __name__ == "__main__":
    check_chile()
