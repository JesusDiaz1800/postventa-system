import logging
from celery import shared_task
from .sap_transaction_service import SAPTransactionService

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,  # 1 minuto
    name='apps.sap_integration.tasks.upload_attachment_to_sap_task'
)
def upload_attachment_to_sap_task(self, call_id, file_path, filename, user_id=None):
    """
    Tarea de Celery para subir un archivo a una llamada de servicio en SAP.
    """
    logger.info(f"Iniciando tarea Celery: Subiendo {filename} a SAP (SC {call_id})")
    
    try:
        user = None
        if user_id:
            from apps.users.models import User
            user = User.objects.filter(id=user_id).first()
            
        sap_service = SAPTransactionService(request_user=user)
        result = sap_service.upload_attachment_to_service_call(
            call_id=call_id,
            file_path=file_path,
            filename=filename,
            replace_if_exists=True  # Usamos nuestra nueva lógica de reemplazo
        )
        
        if result.get('success'):
            logger.info(f"Celery: Subida a SAP exitosa para {filename} (SC {call_id})")
            return f"Success: {filename} uploaded to SC {call_id}"
        else:
            error_msg = result.get('error', 'Unknown Error')
            logger.error(f"Celery: Error subiendo {filename} a SAP: {error_msg}")
            
            # Reintentar si es un error que podría ser temporal (ej: 504 Gateway Timeout, 502, 401)
            # No reintentar si es 400 (Bad Request) o 404 (Not Found)
            if any(tmp in str(error_msg) for tmp in ['500', '502', '503', '504', '401', 'ConnectionError', 'Timeout']):
                logger.info(f"Celery: Reintentando tarea por error temporal...")
                raise self.retry(exc=Exception(error_msg), countdown=60 * (self.request.retries + 1))
            
            return f"Failed: {error_msg}"
            
    except Exception as e:
        logger.exception(f"Celery: Excepción crítica en upload_attachment_to_sap_task: {e}")
        # Reintentar para cualquier excepción no capturada que parezca de red/infra
        raise self.retry(exc=e, countdown=120)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    name='apps.sap_integration.tasks.update_service_call_from_visit_report_task'
)
def update_service_call_from_visit_report_task(self, visit_report_id):
    """
    Sincroniza los campos de texto y UDFs de un VisitReport con la Service Call vinculada en SAP.
    """
    logger.info(f"Iniciando tarea Celery: Sincronizando datos de VisitReport {visit_report_id} a SAP")
    
    try:
        from apps.documents.models import VisitReport
        report = VisitReport.objects.select_related('created_by').get(id=visit_report_id)
        
        sap_service = SAPTransactionService(request_user=report.created_by)
        result = sap_service.update_service_call_from_visit_report(report)
        
        if result.get('success'):
            logger.info(f"Celery: Sincronización de datos exitosa para VR {report.report_number} (SC {report.sap_call_id})")
            return f"Success: VR {report.report_number} data synced to SC {report.sap_call_id}"
        else:
            error_msg = result.get('error', 'Unknown Error')
            logger.error(f"Celery: Error sincronizando datos de VR {report.report_number}: {error_msg}")
            
            if any(tmp in str(error_msg) for tmp in ['500', '502', '503', '504', '401', 'ConnectionError', 'Timeout']):
                 raise self.retry(exc=Exception(error_msg), countdown=60 * (self.request.retries + 1))
            
            return f"Failed: {error_msg}"
            
    except VisitReport.DoesNotExist:
        logger.error(f"Celery: VisitReport {visit_report_id} no encontrado")
        return f"Error: VisitReport {visit_report_id} not found"
    except Exception as e:
        logger.exception(f"Celery: Excepción crítica en update_service_call_from_visit_report_task: {e}")
        raise self.retry(exc=e, countdown=300)
