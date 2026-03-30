import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
import django; django.setup()

from apps.documents.serializers import VisitReportCreateSerializer
from apps.documents.models import VisitReport
from apps.incidents.models import Incident

def test_serializer():
    print("Testing VisitReportCreateSerializer with materials_data...")
    
    # Mock data
    data = {
        'report_number': 'TEST-001',
        'order_number': 'ORD-001',
        'project_name': 'Test Project',
        'materials_data': json.dumps([
            {'material': 'Tube 20mm', 'quantity': 10, 'brand': 'Polifusion', 'lot': 'LOT123'}
        ]),
        'machine_data': json.dumps({'machines': []}),
        'related_incident_id': Incident.objects.first().id if Incident.objects.exists() else None
    }
    
    serializer = VisitReportCreateSerializer(data=data)
    if serializer.is_valid():
        print("[SUCCESS] Serializer is valid")
        validated_data = serializer.validated_data
        print(f"Materials Data (type {type(validated_data.get('materials_data'))}): {validated_data.get('materials_data')}")
        
        if isinstance(validated_data.get('materials_data'), list):
            print("[SUCCESS] materials_data correctly converted to list")
        else:
            print("[FAILURE] materials_data is NOT a list")
    else:
        print("[FAILURE] Serializer errors:", serializer.errors)

if __name__ == "__main__":
    test_serializer()
