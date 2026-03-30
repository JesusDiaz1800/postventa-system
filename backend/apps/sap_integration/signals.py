import logging
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from apps.incidents.models import IncidentImage
from apps.documents.models import DocumentAttachment, QualityReport, SupplierReport, VisitReport
from .tasks import upload_attachment_to_sap_task
from apps.core.thread_local import get_current_country, set_current_country, clear_current_country

logger = logging.getLogger(__name__)

@receiver(post_save, sender=IncidentImage)
def upload_incident_image_to_sap(sender, instance, created, **kwargs):
    """
    Sincroniza la foto (IncidentImage) con la Service Call de SAP vía Celery.
    """
    if not created:
         return
         
    incident = instance.incident
    if not incident or not incident.sap_call_id:
        return
        
    call_id = incident.sap_call_id
    filename = instance.filename
    # Construir ruta base hacia shared documents
    file_path = os.path.join(settings.SHARED_DOCUMENTS_PATH, str(instance.path).lstrip('/'))
    
    if os.path.exists(file_path):
        import threading
        country = get_current_country()
        def thread_wrapper():
            set_current_country(country)
            try:
                user_id = instance.uploaded_by_id if hasattr(instance, 'uploaded_by_id') else None
                upload_attachment_to_sap_task(call_id, file_path, filename, user_id=user_id)
            finally:
                clear_current_country()

        logger.info(f"Iniciando hilo de fondo [{country}] para subir imagen {filename} a SC {call_id}.")
        thread = threading.Thread(target=thread_wrapper)
        thread.daemon = True
        thread.start()
    else:
        logger.warning(f"Señal de SAP ignorada para {filename}: el archivo físico no se encuentra en {file_path}")

@receiver(post_save, sender=DocumentAttachment)
def upload_document_attachment_to_sap(sender, instance, created, **kwargs):
    """
    Sincroniza un DocumentAttachment a SAP vía Celery.
    """
    if not created or not instance.file:
         return
         
    # Determinar el objeto padre según el tipo de documento
    call_id = None
    filename = instance.filename or os.path.basename(instance.file.name)
    file_path = instance.file.path

    if instance.document_type == 'incident_attachment':
        from apps.incidents.models import Incident
        try:
             incident = Incident.objects.get(id=instance.document_id)
             if incident.sap_call_id:
                 call_id = incident.sap_call_id
        except Incident.DoesNotExist:
             pass
             
    elif instance.document_type == 'visit_report':
        from apps.documents.models import VisitReport
        try:
            report = VisitReport.objects.get(id=instance.document_id)
            if report.sap_call_id:
                 call_id = report.sap_call_id
        except VisitReport.DoesNotExist:
            pass
            
    # Si tenemos un call_id válido, encolamos en segundo plano mediante hilos
    if call_id and os.path.exists(file_path):
        import threading
        country = get_current_country()
        def thread_wrapper():
            set_current_country(country)
            try:
                user_id = instance.uploaded_by_id if hasattr(instance, 'uploaded_by_id') else None
                upload_attachment_to_sap_task(call_id, file_path, filename, user_id=user_id)
            finally:
                clear_current_country()

        logger.info(f"Iniciando hilo de fondo [{country}] para subir adjunto {filename} a SC {call_id}.")
        thread = threading.Thread(target=thread_wrapper)
        thread.daemon = True
        thread.start()

@receiver(post_save, sender=QualityReport)
@receiver(post_save, sender=SupplierReport)
# VisitReport se elimina de aquí porque ReportSyncService ya maneja la subida del PDF
def upload_report_pdf_to_sap(sender, instance, created, **kwargs):
    """
    Sincroniza el PDF de un reporte funcional (Calidad o Proveedor) a SAP vía Celery.
    """
    # Evitar recursión si solo estamos actualizando campos de control
    update_fields = kwargs.get('update_fields')
    if update_fields and all(f in ['sync_status', 'last_synced_at', 'pdf_path', 'pdf_file'] for f in update_fields):
        return

    # 1. Verificar si existe la ruta del PDF
    pdf_path = getattr(instance, 'pdf_path', None)
    if not pdf_path:
        pdf_file = getattr(instance, 'pdf_file', None)
        if pdf_file and hasattr(pdf_file, 'path'):
            pdf_path = pdf_file.path
            
    if not pdf_path or not os.path.exists(pdf_path):
        return

    # 2. Obtener el sap_call_id
    call_id = getattr(instance, 'sap_call_id', None)
    if not call_id:
        incident = getattr(instance, 'related_incident', None)
        if incident:
            call_id = incident.sap_call_id
    
    if not call_id:
        logger.debug(f"Sincronización SAP omitida para {instance}: no se encontró sap_call_id")
        return

    # 3. Iniciar subida en hilo de fondo
    import threading
    country = get_current_country()
    def thread_wrapper():
        set_current_country(country)
        try:
            filename = os.path.basename(pdf_path)
            user_id = instance.created_by_id if hasattr(instance, 'created_by_id') else None
            upload_attachment_to_sap_task(call_id, pdf_path, filename, user_id=user_id)
        finally:
            clear_current_country()

    logger.info(f"Iniciando hilo de fondo [{country}] para subir reporte PDF (SC {call_id}).")
    thread = threading.Thread(target=thread_wrapper)
    thread.daemon = True
    thread.start()

# La señal sync_visit_report_data_to_sap_signal se elimina completamente
# porque ReportSyncService ya sincroniza todos los UDFs de forma consolidada.
