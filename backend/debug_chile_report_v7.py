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
from apps.incidents.models import Incident
from apps.audit.models import AuditLog
from django.db.models import Q

def check_recent():
    set_current_country('CL')
    # Get last incident
    inc = Incident.objects.get(code='INC-2026-0016')
    print(f"Incident {inc.code} (ID: {inc.id})")
    print(f"SAP DocNum: {inc.sap_doc_num}, SAP CallID: {inc.sap_call_id}")
    print(f"Status: {inc.estado}")
    
    # Check for report
    report = VisitReport.objects.filter(related_incident=inc).first()
    if report:
        print(f"Visit Report found: {report.report_number} (ID: {report.id})")
        print(f"PDF File: {report.pdf_file}")
        print(f"Sync Status: {report.sync_status}")
        if report.pdf_file:
            print(f"File exists: {os.path.exists(report.pdf_file.path)}")
    else:
        print("NO VISIT REPORT FOUND for this incident.")

    # Check AuditLogs for 24901 or INC-2026-0016
    print("\nLogs for DocNum 24901 or INC-2026-0016:")
    logs = AuditLog.objects.filter(
        Q(description__icontains='24901') | 
        Q(description__icontains='INC-2026-0016')
    ).order_by('-timestamp')
    for l in logs:
        print(f"[{l.timestamp}] {l.action}: {l.description}")
        if l.details:
            print(f"   Details: {l.details}")

if __name__ == "__main__":
    check_recent()
