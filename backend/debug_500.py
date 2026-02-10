import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.audit.models import AuditLog, DeletedItem
from apps.audit.serializers import AuditLogSerializer

def debug_audit_logs():
    print("Fetching last 5 audit logs...")
    logs = AuditLog.objects.all().order_by('-timestamp')[:5]
    
    for log in logs:
        print(f"Log ID: {log.id}, Action: {log.action}")
        try:
            serializer = AuditLogSerializer(log)
            print(f"Serialized: {serializer.data}")
        except Exception as e:
            print(f"ERROR serializing log {log.id}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_audit_logs()
