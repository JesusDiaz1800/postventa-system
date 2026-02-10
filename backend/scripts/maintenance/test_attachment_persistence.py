import os
import sys
import django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(backend_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.incidents.models import Incident, IncidentAttachment
from apps.users.models import User

def test_attachment_persistence_on_close():
    print("Testing attachment persistence on incident close...")

    # 1. Create a test user
    user, _ = User.objects.get_or_create(username='test_user', defaults={'email': 'test@example.com'})
    print(f"User: {user.username}")

    # 2. Create a test incident
    incident = Incident.objects.create(
        code='TEST-INC-001',
        cliente='Cliente Test',
        provider='Proveedor Test',
        created_by=user,
        fecha_deteccion='2025-01-01',
        hora_deteccion='12:00',
        descripcion='Incidencia de prueba'
    )
    print(f"Incident created: {incident.code}")

    # 3. Create a dummy attachment
    dummy_file = SimpleUploadedFile("test_closure_doc.pdf", b"dummy content", content_type="application/pdf")
    
    # 4. Create IncidentAttachment (simulating uploadAttachment endpoint)
    # Note: We simulate the 'file_path' being stored as relative path
    attachment = IncidentAttachment.objects.create(
        incident=incident,
        file_name="test_closure_doc.pdf",
        file_path="incidents/TEST-INC-001/attachments/test_closure_doc.pdf", # Simulated path
        file_size=1024,
        file_type="document",
        mime_type="application/pdf",
        uploaded_by=user
    )
    print(f"Attachment created: {attachment.file_path}")

    # 5. Simulate Close Incident (Scenario 1: Frontend sends just filename)
    print("\nScenario 1: Frontend sends simple filename (current bug simulation)")
    incident.close(
        user=user,
        stage='incidencia',
        summary='Cierre de prueba con fix',
        attachment_path='test_closure_doc.pdf' 
    )
    
    # Refresh from DB
    incident.refresh_from_db()
    print(f"Closure Attachment Path (DB): {incident.closure_attachment}")
    
    # Assertion 1: Should have resolved to full path
    if incident.closure_attachment == attachment.file_path:
        print("✅ SUCCESS: Filename automatically resolved to full path!")
    else:
        print(f"❌ FAILURE: Expected {attachment.file_path}, got {incident.closure_attachment}")

    # 6. Simulate Close Incident (Scenario 2: Auto-link generated report)
    print("\nScenario 2: No attachment provided, but VisitReport exists")
    # Reset
    incident.closure_attachment = ''
    incident.save()
    
    # Create dummy visit report (if VisitReport model exists and matches assumptions)
    try:
        from apps.documents.models import VisitReport
        # Check defaults
        vr = VisitReport.objects.create(
            related_incident=incident,
            visit_date=timezone.now(),
            report_number='TEST-RV-001',
            project_name='Test Project',
            client_name='Test Client',
            technician_name='Tech',
            visit_type='Inspection',
            observations='Obs',
        )
        # Assign a dummy PDF path manually
        vr.pdf_file.name = 'visit_reports/TEST-RV-001.pdf'
        vr.save()
        
        # Close without attachment
        incident.close(
            user=user,
            stage='incidencia',
            summary='Cierre con auto-link',
            attachment_path=''
        )
        
        incident.refresh_from_db()
        print(f"Closure Attachment Path (DB): {incident.closure_attachment}")
        
        if incident.closure_attachment == 'visit_reports/TEST-RV-001.pdf':
            print("✅ SUCCESS: Auto-linked generated Visit Report PDF!")
        else:
            print(f"❌ FAILURE: Expected visit_reports/TEST-RV-001.pdf, got {incident.closure_attachment}")

    except ImportError:
        print("Skipping Scenario 2: VisitReport model not accessible or dependencies missing.")
    except Exception as e:
        print(f"Scenario 2 failed with error: {e}")


    # Cleanup
    incident.delete()
    # User cleanup skipped
    print("\nTest Complete.")

if __name__ == '__main__':
    from django.utils import timezone
    try:
        test_attachment_persistence_on_close()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
