import sys
import os
import django
import io

# Configurar entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

from apps.documents.models import VisitReport
from apps.documents.serializers import VisitReportSerializer
from apps.documents.services.professional_pdf_generator import ProfessionalPDFGenerator
from apps.incidents.models import Incident
from django.contrib.auth import get_user_model

User = get_user_model()

def test_pdf_generation():
    print("Starting PDF generation test...")
    
    # Get or create dummy data
    incident = Incident.objects.first()
    if not incident:
        print("No incident found to test with.")
        return

    # test case 1: Real technician name, no ID
    report = VisitReport.objects.create(
        related_incident=incident,
        project_name="Test Project",
        technician="Cristian Peña",
        technician_id=None,
        status='draft',
        order_number="TEST-PDF-01"
    )
    
    print(f"Created report {report.id} with technician 'Cristian Peña'")
    
    try:
        serializer = VisitReportSerializer(report)
        generator = ProfessionalPDFGenerator()
        buffer = io.BytesIO()
        print("Attempting to generate PDF...")
        success = generator.generate_visit_report_pdf(serializer.data, buffer)
        print(f"Generation success: {success}")
    except Exception as e:
        print(f"!!! CRASH in case 1: {e}")
        import traceback
        traceback.print_exc()

    # test case 2: Technician with ID in model (manually set since serializer misses it)
    report2 = VisitReport.objects.create(
        related_incident=incident,
        project_name="Test Project 2",
        technician="Cristian Peña",
        technician_id=123,
        status='draft',
        order_number="TEST-PDF-02"
    )
    print(f"Created report {report2.id} with technician 'Cristian Peña' and ID 123")
    
    try:
        serializer = VisitReportSerializer(report2)
        # Note: serializer.data will NOT have technician_id yet because it's missing from Meta.fields
        generator = ProfessionalPDFGenerator()
        buffer = io.BytesIO()
        print("Attempting to generate PDF for case 2...")
        success = generator.generate_visit_report_pdf(serializer.data, buffer)
        print(f"Generation success: {success}")
    except Exception as e:
        print(f"!!! CRASH in case 2: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
