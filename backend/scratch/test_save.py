import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# Ajustar sys.path para que encuentre 'apps'
import sys
sys.path.append(os.getcwd())

django.setup()

from apps.visits.models import VisitReport, VisitStatus
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

if not user:
    print("No user found")
    sys.exit(1)

print(f"Testing save for user: {user.username}")

try:
    report = VisitReport(
        client_name="Test Client",
        client_rut="C76241151-5", # Un RUT de prueba común
        status=VisitStatus.APPROVED, # Para disparar la sincronización
        created_by=user,
        project_name="Test Project",
        visit_reason="Test"
    )
    report.save()
    print(f"Success! Report Number: {report.report_number}")
    print(f"SAP Call ID: {report.sap_call_id}")
    print(f"Sync Status: {report.sync_status}")
    if report.sync_status == 'error':
        print(f"Sync Error: {report.sync_error_message}")
except Exception as e:
    import traceback
    print("Failed!")
    traceback.print_exc()
