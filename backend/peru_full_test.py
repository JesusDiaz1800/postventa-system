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

def run_peru_test():
    set_current_country('PE')
    print("--- Starting Peru E2E Test (REFINED) ---")
    
    # 1. Ensure a category exists
    category, _ = Category.objects.get_or_create(name="Pruebas Peru", defaults={"sap_problem_type_id": 1})
    
    suffix = random.randint(10000, 99999)
    
    # 2. Create Incident locally
    incident = Incident.objects.create(
        cliente="CLIENTE PRUEBA PERU",
        cliente_rut="20341778051",
        customer_code="CL20341778051",
        obra="OBRA TEST PERU",
        descripcion=f"Prueba E2E #{suffix} - Validación de todos los campos obligatorios.",
        fecha_deteccion=timezone.now().date(),
        hora_deteccion=timezone.now().time(),
        prioridad="media",
        categoria=category
    )
    print(f"Local Incident created: {incident.code}")
    
    # 3. Create Service Call in SAP
    sap = SAPTransactionService()
    sap_res = sap.create_service_call(
        customer_code=incident.customer_code,
        subject=f"E2E Peru Test {suffix}",
        description=incident.descripcion,
        priority=incident.prioridad,
        technician_code=1, # LUIS CUSTODIO
        problem_type=13,   # POST- VENTA
        bp_project_code='1',
    )
    
    if not sap_res.get('success'):
        print(f"SAP Creation Failed: {sap_res.get('error')}")
        return
    
    incident.sap_call_id = sap_res.get('service_call_id')
    incident.sap_doc_num = sap_res.get('doc_num')
    incident.save()
    print(f"SAP Service Call created: {incident.sap_doc_num} (ID: {incident.sap_call_id})")
    
    # 4. Attach Image with UNIQUE filename
    from PIL import Image
    img = Image.new('RGB', (100, 100), color = (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    
    filename = f"test_pe_{suffix}.jpg"
    rel_path = f"PE/incidents/{incident.id}/images/{filename}"
    full_path = os.path.join("C:/Users/jdiaz/Desktop/postventa-system/backend/shared_documents", "PE", "incidents", str(incident.id), "images")
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
    print(f"Image attached: {filename}")
    
    # Sync image to SAP manually for the test
    print(f"Syncing image {filename} to SAP...")
    img_sap_res = sap.upload_attachment_to_service_call(incident.sap_call_id, final_img_path, filename)
    print(f"Image SAP Sync: {img_sap_res.get('success')} {img_sap_res.get('error', '')}")
    
    # 5. Create Visit Report (Populating sap_call_id with DocNum)
    report = VisitReport.objects.create(
        related_incident=incident,
        report_number=f"R-PE-{suffix}",
        order_number=f"O-PE-{suffix}",
        visit_date=timezone.now(),
        technician="LUIS CUSTODIO",
        project_name="PROYECTO E2E",
        client_name="CLIENTE TEST",
        wall_observations="Paredes OK",
        matrix_observations="Matriz OK",
        general_observations="E2E Global OK",
        status=DocumentStatus.DRAFT,
        sap_call_id=incident.sap_doc_num # SE USA DOCNUM PARA RESOLVER DOCENTRY
    )
    print(f"Visit Report created: {report.report_number}")
    
    # 6. Trigger Sync Task directly
    from apps.documents.tasks import sync_visit_report_task
    print("Triggering sync_visit_report_task...")
    task_res = sync_visit_report_task(
        report_id=report.id, 
        attachments_ids=[], 
        country='PE'
    )
    print(f"Sync Task Result: {task_res}")
    
    # 7. Final Verification
    report.refresh_from_db()
    print(f"Final Report Sync Status: {report.sync_status}")
    if report.sync_error_message:
        print(f"Final Sync Error: {report.sync_error_message}")

if __name__ == "__main__":
    run_peru_test()
