import os
import django
import json
from django.utils import timezone
from django.core.files.base import ContentFile
import io
import random

os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.core.settings'
django.setup()

from apps.incidents.models import Incident, IncidentImage, Category
from apps.documents.models import VisitReport, DocumentAttachment, DocumentStatus
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.core.thread_local import set_current_country

def run_chile_test():
    set_current_country('CL')
    print("--- Starting Chile E2E Test ---")
    
    # 1. Category
    category, _ = Category.objects.get_or_create(name="Pruebas Chile", defaults={"sap_problem_type_id": 1})
    
    suffix = random.randint(10000, 99999)
    
    # 2. Local Incident
    incident = Incident.objects.create(
        cliente="IVAN MICHEA",
        cliente_rut="10198172-K",
        customer_code="C10198172-K",
        obra="OBRA CHILE ACTIVA",
        descripcion=f"Prueba E2E Chile #{suffix}.",
        fecha_deteccion=timezone.now().date(),
        hora_deteccion=timezone.now().time(),
        prioridad="media",
        categoria=category
    )
    print(f"Local Incident created: {incident.code}")
    
    # 3. SAP Service Call
    sap = SAPTransactionService()
    sap_res = sap.create_service_call(
        customer_code=incident.customer_code,
        subject=f"E2E Chile Test {suffix}",
        description=incident.descripcion,
        priority=incident.prioridad,
        technician_code=1, # Default Admin Chile
        problem_type=1,   # 01-Visita Tecnica
        bp_project_code='00001',
    )
    
    if not sap_res.get('success'):
        print(f"SAP Creation Failed: {sap_res.get('error')}")
        return
    
    incident.sap_call_id = sap_res.get('service_call_id')
    incident.sap_doc_num = sap_res.get('doc_num')
    incident.save()
    print(f"SAP Service Call created: {incident.sap_doc_num} (ID: {incident.sap_call_id})")
    
    # 4. Image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color = (0, 255, 0))
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    
    filename = f"test_cl_{suffix}.jpg"
    rel_path = f"CL/incidents/{incident.id}/images/{filename}"
    full_path = os.path.join("C:/Users/jdiaz/Desktop/postventa-system/backend/shared_documents", "CL", "incidents", str(incident.id), "images")
    os.makedirs(full_path, exist_ok=True)
    final_img_path = os.path.join(full_path, filename)
    with open(final_img_path, 'wb+') as f:
        f.write(img_io.getvalue())
        
    img_obj = IncidentImage.objects.create(
        incident=incident,
        filename=filename,
        path=rel_path,
        file_size=len(img_io.getvalue()),
        mime_type="image/jpeg"
    )
    
    print(f"Syncing image to Chile SAP...")
    img_sap_res = sap.upload_attachment_to_service_call(incident.sap_call_id, final_img_path, filename)
    print(f"Image SAP Sync: {img_sap_res.get('success')}")
    
    # 5. Visit Report
    report = VisitReport.objects.create(
        related_incident=incident,
        report_number=f"RV-CL-{suffix}",
        order_number=f"OC-CL-{suffix}",
        visit_date=timezone.now(),
        technician="TECNICO CHILE",
        status=DocumentStatus.DRAFT,
        sap_call_id=incident.sap_doc_num
    )
    print(f"Visit Report created: {report.report_number}")
    
    # 6. Sync
    from apps.documents.tasks import sync_visit_report_task
    print("Triggering sync_visit_report_task...")
    task_res = sync_visit_report_task(
        report_id=report.id, 
        attachments_ids=[], 
        country='CL'
    )
    print(f"Sync Task Result: {task_res}")
    
    report.refresh_from_db()
    print(f"Final Report Sync Status: {report.sync_status}")

if __name__ == "__main__":
    run_chile_test()
