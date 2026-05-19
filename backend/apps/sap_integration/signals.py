import logging
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

@receiver(post_save, sender='documents.DocumentAttachment')
def upload_document_attachment_to_sap(sender, instance, created, **kwargs):
    """
    Sincroniza un DocumentAttachment a SAP vía Celery (solo para Visit Reports).
    """
    from apps.documents.models import DocumentAttachment
    from apps.visits.models import VisitReport
    from .tasks import upload_attachment_to_sap_task
    from apps.core.thread_local import get_current_country, set_current_country, clear_current_country

    if not created or not instance.file:
         return
         
    call_id = None
    filename = instance.filename or os.path.basename(instance.file.name)
    file_path = instance.file.path

    # SERTEC-SYSTEM: Solo procesamos adjuntos vinculados a Reportes de Visita
    if instance.document_type == 'visit_report':
        try:
            report = VisitReport.objects.using(instance._state.db).get(id=instance.document_id)
            if report.sap_call_id:
                 call_id = report.sap_call_id
        except Exception:
            pass
            
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
