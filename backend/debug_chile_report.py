import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.reports.models import VisitReport
from apps.audit.models import AuditLog
from django.db.models import Q

def check_chile():
    print("=== INVESTIGATING CHILE VISIT REPORT PDF ===")
    
    # 1. Get last report for Chile
    last_report = VisitReport.objects.filter(incident__country='CL').order_by('-created_at').first()
    
    if not last_report:
        print("No VisitReports found for Chile.")
        return

    print(f"Latest Report Found:")
    print(f" - ID: {last_report.id}")
    print(f" - Incident: {last_report.incident.code}")
    print(f" - Created at: {last_report.created_at}")
    print(f" - PDF file field: {last_report.pdf_file}")
    
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
    print("\nRecent Audit Logs for this report or 'Report' in general:")
    logs = AuditLog.objects.filter(
        Q(description__icontains=str(last_report.id)) | 
        Q(description__icontains='Report') |
        Q(action__icontains='sap')
    ).order_by('-created_at')[:15]
    
    for l in logs:
        print(f"[{l.created_at}] {l.action}: {l.description}")
        if l.details:
            print(f"   Details: {l.details}")

if __name__ == "__main__":
    check_chile()
