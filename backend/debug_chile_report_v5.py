import os
import django
import sys

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.core.thread_local import set_current_country
from apps.documents.models import VisitReport
from apps.audit.models import AuditLog
from django.db.models import Q

def check_chile():
    set_current_country('CL')
    report = VisitReport.objects.all().order_by('-created_at').first()
    
    if not report:
        print("No report.")
        return

    print(f"Report {report.report_number} (ID: {report.id})")
    print(f"PDF File: {report.pdf_file}")
    if report.pdf_file:
        print(f"File exists: {os.path.exists(report.pdf_file.path)}")
    
    # Corrected AuditLog Query
    print("\nLogs:")
    logs = AuditLog.objects.filter(
        Q(description__icontains=report.report_number) | 
        Q(description__icontains=str(report.id))
    ).order_by('-timestamp')[:10]
    
    for l in logs:
        print(f"[{l.timestamp}] {l.action}: {l.description}")
        if l.details:
            print(f"   Details: {l.details}")

if __name__ == "__main__":
    check_chile()
