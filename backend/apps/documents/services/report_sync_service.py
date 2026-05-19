import logging
import threading
import json
import io
import os
from django.utils import timezone
from django.core.files.base import ContentFile
from apps.documents.models import VisitReport, DocumentAttachment
from apps.sap_integration.sap_transaction_service import SAPTransactionService
from apps.sap_integration.sap_query_service import SAPQueryService
from apps.documents.services.professional_pdf_generator import ProfessionalPDFGenerator
from apps.documents.serializers import VisitReportSerializer

logger = logging.getLogger(__name__)

class ReportSyncService:
    """
    Service to handle background synchronization of Visit Reports with SAP
    and PDF regeneration.
    """
    
    @staticmethod
    def sync_report_async(report_id, attachments_ids=None, img_descriptions=None, has_manual_pdf=False, user=None):
        """
        Encola una tarea de sincronización completa para el reporte.
        Intenta usar Celery, pero hace fallback a threading.Thread para asegurar fluidez en Windows.
        """
        from apps.documents.tasks import sync_visit_report_task
        from apps.core.thread_local import get_current_country, set_current_country, clear_current_country
        from django.conf import settings
        import threading
        
        attachments_ids = attachments_ids or []
        img_descriptions = img_descriptions or {}
        country = get_current_country()
        user_id = user.id if user else None

        # Si estamos en modo EAGER (típico de Windows dev) o falla Celery, usar hilos directamente
        is_eager = getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)
        
        if not is_eager:
            try:
                logger.info(f"Encolando tarea de Celery para reporte {report_id} [{country}]")
                sync_visit_report_task.delay(
                    report_id, 
                    attachments_ids, 
                    img_descriptions, 
                    has_manual_pdf, 
                    user_id,
                    country=country
                )
                return True
            except Exception as e:
                logger.warning(f"Error al encolar en Celery, haciendo fallback a hilo: {e}")
        
        # Fallback a hilo para asegurar que la UI no se bloquee ni falle
        try:
            logger.info(f"Iniciando hilo de fondo para sincronización de reporte {report_id} [{country}]")
            
            def thread_wrapper():
                try:
                    set_current_country(country)
                    ReportSyncService._sync_process(report_id, attachments_ids, img_descriptions, has_manual_pdf, user_id)
                except Exception as thread_err:
                    logger.error(f"Error asíncrono en hilo de sincronización para reporte {report_id}: {thread_err}", exc_info=True)
                finally:
                    clear_current_country()

            thread = threading.Thread(
                target=thread_wrapper,
                daemon=True
            )
            thread.start()
            return True
        except Exception as e:
            logger.error(f"Error fatal iniciando hilo de sincronización para reporte {report_id}: {e}")
            return False

    @staticmethod
    def _sync_process(report_id, attachments_ids, img_descriptions, has_manual_pdf, user_id):
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id) if user_id else None
            
            report = VisitReport.objects.get(id=report_id)
            sap_tx = SAPTransactionService(request_user=user)
            sap_query = SAPQueryService()
            
            # 1. Regenerate PDF locally FIRST (Ensure availability even if SAP fails)
            logger.info(f"Generating local PDF for report {report.report_number}...")
            ReportSyncService._regenerate_and_upload_pdf(report, None, None, has_manual_pdf)
            
            # 2. Resolve DocNum to internal CallID (DocEntry)
            internal_call_id = ReportSyncService._resolve_internal_call_id(report, sap_query)
            
            if not internal_call_id:
                logger.warning(f"SAP ID resolution pending for {report.report_number}. Local PDF remains available.")
                return

            # 3. Update SAP UDFs
            ReportSyncService._update_sap_udfs(report, internal_call_id, sap_tx, sap_query)
            
            # 3. Import SAP Attachments (Disabled to avoid duplicate incident images)
            # ReportSyncService._import_sap_attachments(report, internal_call_id, sap_query, img_descriptions, user)

            
            # 4. Upload new local attachments to SAP
            for att_id in attachments_ids:
                try:
                    att = DocumentAttachment.objects.get(id=att_id)
                    sap_tx.upload_attachment_to_service_call(internal_call_id, att.file.path, att.filename)
                except Exception as up_err:
                    logger.error(f"Async SAP Upload Error for attachment {att_id}: {up_err}")

            # 5. Upload PDF to SAP (since we already have it locally)
            ReportSyncService._regenerate_and_upload_pdf(report, internal_call_id, sap_tx, has_manual_pdf)
            
            # 6. Update Sync Status
            try:
                report.sync_status = 'synced'
                report.last_synced_at = timezone.now()
                report.save(update_fields=['sync_status', 'last_synced_at'])
            except Exception as e:
                # Si el reporte fue eliminado (ej. en cascada) mientras sincronizábamos
                logger.warning(f"No se pudo actualizar estado final del reporte {report_id}: {e}")
            
        except Exception as e:
            logger.error(f"CRITICAL ReportSyncService Error for report {report_id}: {e}", exc_info=True)
            try:
                report = VisitReport.objects.get(id=report_id)
                report.sync_status = 'error'
                report.sync_error_message = str(e)
                report.save(update_fields=['sync_status', 'sync_error_message'])
            except:
                pass

    @staticmethod
    def _resolve_internal_call_id(report, sap_query):
        if not report.sap_call_id:
            return None
            
        stored_id = report.sap_call_id
        internal_call_id = None
        
        # Try via query service (HANA API)
        try:
            call_data = sap_query.get_service_call(stored_id)
            if call_data and 'call_id' in call_data:
                internal_call_id = call_data['call_id']
                logger.info(f"[SAP-OK] DocNum {stored_id} resuelto a CallID {internal_call_id}")
        except Exception as e:
            logger.error(f"Error resolving CallID via API: {e}")
            
        # Fallback to direct SQL
        if not internal_call_id:
            try:
                from django.db import connections
                db_alias = sap_query._get_db_alias()
                with connections[db_alias].cursor() as cursor:
                    cursor.execute("SELECT callID FROM OSCL WHERE DocNum = %s", [stored_id])
                    row = cursor.fetchone()
                    if row:
                        internal_call_id = row[0]
                        logger.info(f"[SAP-OK] Fallback SQL: DocNum {stored_id} -> CallID {internal_call_id}")
            except Exception as sql_err:
                logger.error(f"Fallback SQL failed: {sql_err}")
                
        return internal_call_id

    @staticmethod
    def _update_sap_udfs(report, internal_call_id, sap_tx, sap_query):
        patch_payload = {}
        
        # Obtener campos disponibles en SAP para Service Calls (OSCL)
        available_udfs = sap_query.get_available_udfs('OSCL')
        logger.info(f"SAP: Campos disponibles para filtrado dinámico: {len(available_udfs)}")
        
        # Map fields (Solo agregar si tienen contenido para evitar borrar datos en SAP)
        obs_fields = [
            ("U_NX_OBS_MURO", report.wall_observations),
            ("U_NX_OBS_MATRIZ", report.matrix_observations),
            ("U_NX_OBS_LOSA", report.slab_observations),
            ("U_NX_OBS_ALMAC", report.storage_observations),
            ("U_NX_OBS_PRE_ARM", report.pre_assembled_observations),
            ("U_NX_OBS_EXTER", report.exterior_observations),
            ("U_NX_GENE", report.general_observations),
        ]
        
        for sap_field, value in obs_fields:
            if value and str(value).strip():
                # Proteccion heurística: No enviar si el valor parece ser el resumen de cierre (Resolution)
                val_str = str(value)
                if sap_field == "U_NX_GENE" and ("[Motivo:" in val_str or "[CIERRE DETALLADO]" in val_str):
                    logger.warning(f"Protección U_NX_GENE (Async) activada: Se detectó patrón de resolución ('{val_str[:20]}...'). Saltando.")
                    continue
                
                patch_payload[sap_field] = val_str[:254]
        
        machine_data = report.machine_data or {}
        if machine_data.get('machine_removal'): patch_payload["U_NX_RET_MQ"] = 1
        elif 'machine_removal' in machine_data: patch_payload["U_NX_RET_MQ"] = 0
            
        machines = machine_data.get('machines', [])
        for i in range(min(len(machines), 6)):
            idx = i + 1
            machine = machines[i]
            if machine.get('machine'): patch_payload[f"U_NX_MAQ{idx}"] = str(machine['machine'])[:100]
            if machine.get('start'): 
                try: patch_payload[f"U_NX_INI{idx}"] = int(machine['start'])
                except ValueError: pass
            if machine.get('cut'):
                try: patch_payload[f"U_NX_COR{idx}"] = int(machine['cut'])
                except ValueError: pass
        
        # Sincronizar Técnico si está definido en el reporte
        if report.technician_id:
            try:
                patch_payload["TechnicianCode"] = int(report.technician_id)
            except (ValueError, TypeError):
                pass
            
        from apps.core.thread_local import get_current_country
        country = get_current_country()
        
        sap_meta = machine_data.get('sap_metadata', {})
        if 'is_mixed_material' in sap_meta: patch_payload["U_NX_MEZCLADO"] = 1 if sap_meta['is_mixed_material'] else 0
        if 'is_rescued_project' in sap_meta: patch_payload["U_NX_RESCATADA"] = 1 if sap_meta['is_rescued_project'] else 0
        if 'patent_number' in sap_meta and sap_meta['patent_number']: patch_payload["U_NX_PATENTE"] = str(sap_meta['patent_number'])[:100]
        if 'is_project_finished' in sap_meta: patch_payload["U_NX_OBRAFINALIZADA"] = 1 if sap_meta['is_project_finished'] else 0
        
        if 'project_with_other_provider' in sap_meta and country == 'CL':
            val = sap_meta['project_with_other_provider']
            patch_payload["U_obra_con_otro_proveedor"] = "1" if str(val).upper() in ('SI', 'SÍ', '1', 'TRUE') else "0"
            
        if 'installation_level' in sap_meta and country == 'CL':
            level_map = {'NORMAL': '0', 'DEFICIENTE': '1'}
            val = str(sap_meta['installation_level']).upper()
            patch_payload["U_nivel_instalacion"] = level_map.get(val, '0')
            
        if 'other_provider' in sap_meta and sap_meta['other_provider'] and country == 'CL': patch_payload["U_otro_proveedor"] = str(sap_meta['other_provider'])[:100]
        if report.visit_date: patch_payload["U_NX_FECHAVISITA"] = report.visit_date.strftime('%Y-%m-%d')
        
        # Sincronizar Técnico de SAP
        if report.technician_id:
            try:
                patch_payload["TechnicianCode"] = int(report.technician_id)
            except (ValueError, TypeError):
                pass
        
        try:
            patch_payload["U_NX_NREPORT"] = int(report.report_number.split('-')[-1])
        except: pass

        # Sincronizar Categoría y SubCategoría (Dinámico: Solo si existen en SAP)
        if hasattr(report, 'related_incident') and report.related_incident:
            incident = report.related_incident
            
            # Solo enviar si el campo existe físicamente en el esquema de SAP local
            if 'U_is_categoria' in available_udfs:
                if getattr(incident, 'categoria', None):
                    patch_payload["U_is_categoria"] = str(incident.categoria.name)[:100]
                else:
                    patch_payload["U_is_categoria"] = "" # Limpiar si no hay categoría
            
            if 'U_is_subcategoria' in available_udfs:
                if getattr(incident, 'subcategoria', None):
                    patch_payload["U_is_subcategoria"] = str(incident.subcategoria)[:100]
                else:
                    patch_payload["U_is_subcategoria"] = "" # Limpiar si no hay subcategoría

        if patch_payload:
            logger.info(f"[SAP-SYNC] Updating UDFs for CallID {internal_call_id}")
            logger.info(f"[SAP-SYNC] Payload: {json.dumps(patch_payload, indent=2)}")
            
            res = sap_tx.update_service_call(internal_call_id, patch_payload)
            
            # Lógica de Reintento si falla por el rol de Técnico (Error frecuente en TSTPOLPERU y TSTPOLCOLOMBIA)
            if not res.get('success') and 'TechnicianCode' in patch_payload:
                error_msg = str(res.get('error', '')).lower()
                if 'technician' in error_msg or '-5002' in error_msg:
                    logger.warning(f"[SAP-SYNC] El empleado {report.technician_id} NO tiene el rol de técnico en SAP. Saltando TechnicianCode para permitir el resto de la sincronización.")
                    del patch_payload["TechnicianCode"]
                    res = sap_tx.update_service_call(internal_call_id, patch_payload)
            
            if not res.get('success'):
                logger.error(f"[SAP-SYNC] Failed to update UDFs for CallID {internal_call_id}: {res.get('error')}")
            else:
                logger.info(f"[SAP-SYNC] UDFs updated successfully for CallID {internal_call_id}")
        else:
            logger.warning(f"[SAP-SYNC] No UDF data to update for Report {report.id}")

    @staticmethod
    def _import_sap_attachments(report, internal_call_id, sap_query, custom_descriptions, user):
        attachments = sap_query.get_attachments(report.sap_call_id) # Uses DocNum
        if not attachments:
            return
            
        for attach in attachments:
            try:
                # Check if already imported
                filename = attach['filename']
                if DocumentAttachment.objects.filter(document_type='visit_report', document_id=report.id, filename=filename).exists():
                    continue
                    
                content, mime_type, _ = sap_query.get_attachment_file(attach['atc_entry'], attach['line'])
                if content:
                    import os
                    file_base = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
                    description = custom_descriptions.get(filename, file_base)
                    
                    doc_att = DocumentAttachment(
                        document_type='visit_report',
                        document_id=report.id,
                        filename=filename,
                        file_type=mime_type,
                        file_size=len(content),
                        description=description,
                        uploaded_by=user
                    )
                    doc_att.file.save(filename, ContentFile(content), save=True)
            except Exception as e:
                logger.error(f"Error importing SAP attachment {attach.get('filename')}: {e}")

    @staticmethod
    def _regenerate_and_upload_pdf(report, internal_call_id=None, sap_tx=None, has_manual_pdf=False):
        if has_manual_pdf:
            # Just upload existing PDF
            if report.pdf_file:
                fn = f"reporte_visita_{report.report_number}.pdf"
                sap_tx.upload_attachment_to_service_call(internal_call_id, report.pdf_file.path, fn)
            return

        try:
            report.refresh_from_db()
            serializer = VisitReportSerializer(report)
            generator = ProfessionalPDFGenerator()
            pdf_buffer = io.BytesIO()
            
            if generator.generate_visit_report_pdf(serializer.data, pdf_buffer):
                fn = f"reporte_visita_{report.report_number}.pdf"
                report.pdf_file.save(fn, ContentFile(pdf_buffer.getvalue()), save=True)
                
                # Upload to SAP only if we have the ID and transaction service
                if internal_call_id and sap_tx:
                    sap_tx.upload_attachment_to_service_call(internal_call_id, report.pdf_file.path, fn)
                    logger.info("[SAP-OK] PDF uploaded to SAP")
                else:
                    logger.info("[LOCAL-OK] PDF saved locally (SAP sync deferred)")
        except Exception as e:
            logger.error(f"Error regenerating PDF: {e}")
