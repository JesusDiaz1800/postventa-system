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
from apps.documents.models import VisitReport
from apps.documents.services.report_sync_service import ReportSyncService

def force_sync():
    set_current_country('CL')
    # Report 20263 (RV-2026-072)
    report_id = 20263
    print(f"Forcing sync for Report {report_id}...")
    
    # Triggering the sync process manually
    # Signature: _sync_process(report_id, attachments_ids, img_descriptions, has_manual_pdf, user_id)
    ReportSyncService._sync_process(report_id, [], [], False, None)
    
    # Check AuditLog for last 5 mins
    from apps.audit.models import AuditLog
    from django.utils import timezone
    from datetime import timedelta
    
    print("\nRecent Audit Logs:")
    recent = timezone.now() - timedelta(minutes=5)
    logs = AuditLog.objects.filter(timestamp__gte=recent).order_by('-timestamp')
    for l in logs:
        print(f"[{l.timestamp}] {l.action}: {l.description}")
        if l.details:
            print(f"   Details: {l.details}")

if __name__ == "__main__":
    force_sync()
