from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import base64
import traceback
from apps.core.thread_local import get_current_country

User = get_user_model()

class VisitStatus(models.TextChoices):
    DRAFT = 'draft', 'Borrador'
    PENDING_REVIEW = 'pending_review', 'Pendiente de Revisión'
    APPROVED = 'approved', 'Aprobado'
    SENT = 'sent', 'Enviado'
    WAITING_RESPONSE = 'waiting_response', 'Esperando Respuesta'
    CLOSED = 'closed', 'Cerrado'

class InstallationLevel(models.TextChoices):
    NORMAL = '0', 'Normal'
    DEFICIENTE = '1', 'Deficiente'
    CRITICO = '2', 'Crítico'
    INEXISTENTE = '3', 'Inexistente'
    NO_APLICA = '4', 'No Aplica'

def get_visit_report_pdf_path(instance, filename):
    """Genera ruta dinámica: <pais>/visit_reports/pdfs/YYYY/MM/filename"""
    country = get_current_country()
    year_month = timezone.now().strftime('%Y/%m')
    return f"{country}/visit_reports/pdfs/{year_month}/{filename}"

class VisitReport(models.Model):
    """
    Modelo para reportes de visita técnica (Entidad Principal en SERTEC)
    """
    # Información básica
    report_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Reporte")
    order_number = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Número de Orden")
    visit_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Visita")
    
    # Información del proyecto/cliente
    project_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre del Proyecto")
    project_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID del Proyecto")
    client_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nombre del Cliente")
    client_rut = models.CharField(max_length=20, blank=True, null=True, verbose_name="Código Cliente")
    address = models.TextField(blank=True, null=True, verbose_name="Dirección")
    construction_company = models.CharField(max_length=200, blank=True, verbose_name="Empresa Constructora")
    
    # Personal involucrado
    salesperson = models.CharField(max_length=100, blank=True, null=True, verbose_name="Vendedor")
    technician = models.CharField(max_length=100, blank=True, null=True, verbose_name="Técnico")
    technician_id = models.IntegerField(null=True, blank=True, verbose_name="ID Técnico SAP")
    installer = models.CharField(max_length=100, blank=True, verbose_name="Instalador")
    installer_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono del Instalador")
    
    # Personal adicional (campos SAP)
    professional_name = models.CharField(max_length=100, blank=True, verbose_name="Profesional de Obra")
    
    # Datos de contacto adicionales
    client_contact = models.CharField(max_length=200, blank=True, verbose_name="Persona de Contacto")
    client_email = models.CharField(max_length=255, blank=True, null=True, verbose_name="Email del Cliente")
    telephone = models.CharField(max_length=50, blank=True, verbose_name="Teléfono Llamada SAP")
    fax = models.CharField(max_length=20, blank=True, verbose_name="Fax")
    contact_observations = models.TextField(blank=True, verbose_name="Observaciones de Contacto")
    
    # Ubicación
    commune = models.CharField(max_length=100, blank=True, null=True, verbose_name="Comuna")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    
    # Motivo de la visita
    visit_reason = models.CharField(max_length=100, default='1', blank=True, null=True, verbose_name="Motivo de la Visita")

    # Información del producto (Persistencia directa para desacople de incidents)
    product_category = models.CharField(max_length=100, blank=True, verbose_name="Categoría Producto")
    product_subcategory = models.CharField(max_length=100, blank=True, verbose_name="Subcategoría Producto")
    product_provider = models.CharField(max_length=100, blank=True, verbose_name="Proveedor")
    
    # Información de la incidencia (Persistencia directa)
    incident_code = models.CharField(max_length=50, blank=True, verbose_name="Código Incidencia")
    incident_description = models.TextField(blank=True, verbose_name="Descripción Incidencia")
    incident_priority = models.CharField(max_length=50, blank=True, verbose_name="Prioridad Incidencia")
    incident_responsible = models.CharField(max_length=100, blank=True, verbose_name="Responsable Incidencia")
    incident_detection_date = models.CharField(max_length=20, blank=True, verbose_name="Fecha Detección")
    incident_detection_time = models.CharField(max_length=20, blank=True, verbose_name="Hora Detección")
    incident_immediate_actions = models.TextField(blank=True, verbose_name="Acciones Inmediatas")
    
    # Datos de máquinas
    machine_data = models.JSONField(default=dict, blank=True, verbose_name="Datos de Máquinas")
    
    # Tabla de materiales (Material, Cantidad, Marca, Lote)
    materials_data = models.JSONField(default=list, blank=True, verbose_name="Tabla de Materiales")
    
    # Observaciones por sección
    wall_observations = models.TextField(blank=True, verbose_name="Observaciones Muro/Tabique")
    matrix_observations = models.TextField(blank=True, verbose_name="Observaciones Matriz")
    slab_observations = models.TextField(blank=True, verbose_name="Observaciones Losa")
    storage_observations = models.TextField(blank=True, verbose_name="Observaciones Almacenaje")
    pre_assembled_observations = models.TextField(blank=True, verbose_name="Observaciones Pre Armados")
    exterior_observations = models.TextField(blank=True, verbose_name="Observaciones Exteriores")
    general_observations = models.TextField(blank=True, verbose_name="Observaciones Generales")
    critical_observations = models.TextField(blank=True, verbose_name="Observación Crítica (Interna)")

    # Metadatos Técnicos SAP (UDFs)
    is_mixed_material = models.BooleanField(default=False, verbose_name="Material Mixto")
    is_rescued_project = models.BooleanField(default=False, verbose_name="Obra Rescatada")
    patent_number = models.CharField(max_length=100, blank=True, verbose_name="Número de Patente")
    is_project_finished = models.BooleanField(default=False, verbose_name="Obra Terminada")
    installation_level = models.CharField(
        max_length=50, 
        choices=InstallationLevel.choices, 
        default=InstallationLevel.NORMAL, 
        verbose_name="Nivel de Instalación"
    )
    is_other_provider = models.BooleanField(default=False, verbose_name="Obra con otro proveedor")
    other_provider_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre del otro proveedor")
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20, 
        choices=VisitStatus.choices, 
        default=VisitStatus.DRAFT,
        verbose_name="Estado",
        db_index=True
    )
    
    # Metadatos
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_visit_reports',
        verbose_name="Creado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    # Archivo PDF generado
    pdf_file = models.FileField(
        upload_to=get_visit_report_pdf_path, 
        null=True, 
        blank=True,
        verbose_name="PDF del Reporte"
    )
    
    # Firmas
    technician_signature = models.TextField(blank=True, null=True, verbose_name="Firma Técnico (Base64)")
    installer_signature = models.TextField(blank=True, null=True, verbose_name="Firma Instalador (Base64)")
    client_signature = models.TextField(blank=True, null=True, verbose_name="Firma del Cliente (Base64)")

    
    # Campos de almacenamiento
    docx_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ruta del documento DOCX")
    pdf_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ruta del documento PDF")


    # Integración SAP
    sap_call_id = models.IntegerField(null=True, blank=True, verbose_name="ID Llamada SAP", db_index=True)
    sap_doc_num = models.IntegerField(null=True, blank=True, verbose_name="DocNum Oficial SAP", db_index=True)
    sync_status = models.CharField(max_length=20, default='pending', verbose_name="Estado Sincronización") # pending, synced, error
    last_synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Última Sincronización")
    sync_error_message = models.TextField(blank=True, null=True, verbose_name="Error Sincronización")
    
    class Meta:
        verbose_name = "Reporte de Visita"
        verbose_name_plural = "Reportes de Visita"
    
    def __str__(self):
        return f"Reporte {self.report_number} - {self.project_name}"
    
    def save(self, *args, **kwargs):
        """
        Guarda el reporte y gestiona la sincronización con SAP Business One.
        """
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        
        try:
            # 1. Saneamiento de campos de texto (Evitar None para SAP)
            text_fields = [
                'client_rut', 'project_id', 'salesperson', 'technician',
                'installer', 'installer_phone', 'professional_name', 'technical_inspector',
                'quality_manager', 'management_manager', 'fax', 'commune', 'city', 'visit_reason',
                'product_category', 'product_subcategory', 'product_provider',
                'incident_code', 'incident_description', 'incident_priority', 'incident_responsible',
                'incident_detection_date', 'incident_detection_time', 'incident_immediate_actions',
                'other_provider_name', 'patent_number', 'telephone'
            ]
            for field in text_fields:
                if getattr(self, field, None) is None:
                    setattr(self, field, '')

            is_new = self.pk is None
            
            # Detectar si cambió la fecha o el técnico para notificaciones
            date_changed = False
            technician_changed = False
            if not is_new:
                try:
                    old_instance = VisitReport.objects.get(pk=self.pk)
                    date_changed = (old_instance.visit_date != self.visit_date)
                    technician_changed = (old_instance.technician != self.technician)
                except VisitReport.DoesNotExist:
                    pass
            
            # 2. Generación de Número de Reporte correlativo
            if not self.report_number:
                year = timezone.now().year
                last = VisitReport.objects.filter(report_number__startswith=f"RV-{year}").exclude(id=self.id).order_by('-report_number').first()
                if last:
                    try:
                        num = int(last.report_number.split('-')[-1]) + 1
                    except: num = 1
                else: num = 1
                self.report_number = f"RV-{year}-{num:03d}"
            
            if not self.order_number or self.order_number == self.report_number or self.order_number.startswith('SAP-None'):
                self.order_number = f"SAP-{self.sap_doc_num}" if self.sap_doc_num else self.report_number
            
            # 3. Guardado en Base de Datos Local
            # Si el estado es APPROVED, nos aseguramos que el pdf_path esté actualizado antes del primer save
            if self.status == VisitStatus.APPROVED and self.pdf_file and not self.pdf_path:
                try:
                    self.pdf_path = self.pdf_file.path
                except: pass

            super().save(*args, **kwargs)
            logger.info(f"Reporte {self.report_number} guardado localmente (ID: {self.id})")
            
            # Enviar notificación por correo al técnico si es nueva visita o cambió fecha/técnico
            if is_new or date_changed or technician_changed:
                try:
                    from django.db import transaction
                    import threading
                    
                    country_code = get_current_country()
                    visit_id = self.id
                    
                    is_new_local = is_new
                    date_changed_local = date_changed
                    technician_changed_local = technician_changed
                    
                    def run_notification():
                        def thread_target():
                            try:
                                from apps.core.thread_local import set_current_country
                                set_current_country(country_code)
                                from apps.documents.services.email_service import EmailService
                                EmailService.send_technician_notification(
                                    visit_id=visit_id,
                                    is_new=is_new_local,
                                    date_changed=date_changed_local,
                                    technician_changed=technician_changed_local
                                )
                            except Exception as th_err:
                                logger.error(f"Error in technician notification thread: {th_err}")
                        
                        t = threading.Thread(target=thread_target, daemon=True)
                        t.start()
                    
                    # Se usa on_commit para asegurar que los datos estén confirmados en la BD
                    # antes de que el hilo de fondo intente leerlos.
                    transaction.on_commit(run_notification)
                    logger.info(f"Notification email to technician scheduled for visit {self.report_number}")
                except Exception as email_err:
                    logger.error(f"Error scheduling technician email: {email_err}")
            
            # 4. Sincronización con SAP (Llamadas de Servicio)
            # Solo si el reporte está APROBADO (Firmado) o CERRADO
            if self.status in (VisitStatus.APPROVED, VisitStatus.CLOSED):
                from apps.sap_integration.sap_transaction_service import SAPTransactionService
                sap_service = SAPTransactionService(request_user=self.created_by)
                
                if not self.sap_call_id:
                    # CASO A: Crear nueva Llamada de Servicio con TODO (UDFs + Anexos)
                    logger.info(f"Iniciando creación de Llamada de Servicio INTEGRAL para {self.report_number}")
                    
                    # A.1 Preparar UDFs de Máquinas y Observaciones
                    udf = {
                        'visit_date':           self.visit_date,
                        'obs_muro':             self.wall_observations,
                        'obs_matriz':           self.matrix_observations,
                        'obs_losa':             self.slab_observations,
                        'obs_almac':            self.storage_observations,
                        'obs_pre_arm':          self.pre_assembled_observations,
                        'obs_exter':            self.exterior_observations,
                        'obs_gene':             self.general_observations,
                        'obs_critica':          self.critical_observations,
                        # Métricas de obra
                        'is_mixed_material':    self.is_mixed_material,
                        'is_rescued_project':   self.is_rescued_project,
                        'is_project_finished':  self.is_project_finished,
                        'installation_level':   self.installation_level,
                        'is_other_provider':    self.is_other_provider,
                        'other_provider_name':  self.other_provider_name,
                        'patent_number':        self.patent_number,
                        # Vendedor
                        'salesperson_name':     self.salesperson,
                    }
                    
                    m_data = self.machine_data or {}
                    machines = m_data.get('machines', [])
                    for i in range(1, 7):
                        if i <= len(machines):
                            m = machines[i-1]
                            udf[f'maq{i}'] = m.get('machine') or m.get('modelo', '')
                            udf[f'ini{i}'] = str(m.get('start') or m.get('inicio', ''))
                            udf[f'cor{i}'] = str(m.get('cut') or m.get('cortes', ''))
                        else:
                            udf[f'maq{i}'] = ""
                            udf[f'ini{i}'] = ""
                            udf[f'cor{i}'] = ""

                    # A.2 Preparar Anexos (Fotos + PDF)
                    attachments = []
                    # 1. El PDF firmado
                    if self.pdf_file:
                        try:
                            pdf_content = None
                            # Intento A: Leer desde el objeto de archivo en memoria (más rápido y seguro en el primer save)
                            try:
                                if hasattr(self.pdf_file, 'file') and self.pdf_file.file:
                                    self.pdf_file.open('rb')
                                    pdf_content = self.pdf_file.read()
                                    self.pdf_file.close()
                                    if pdf_content: logger.info("PDF capturado desde objeto en memoria")
                            except: pass

                            # Intento B: Leer desde el storage (disco) si el Intento A falló
                            if not pdf_content:
                                import time
                                for attempt in range(5):
                                    try:
                                        # Refrescar desde DB por si otro proceso guardó el archivo
                                        self.refresh_from_db(fields=['pdf_file'])
                                        if self.pdf_file and self.pdf_file.storage.exists(self.pdf_file.name):
                                            with self.pdf_file.open('rb') as f:
                                                pdf_content = f.read()
                                                if pdf_content: 
                                                    logger.info(f"PDF capturado desde disco en intento {attempt+1}")
                                                    break
                                    except: pass
                                    time.sleep(1.0)

                            if pdf_content:
                                attachments.append({
                                    'name': f"Reporte_{self.report_number}.pdf",
                                    'content': base64.b64encode(pdf_content).decode()
                                })
                                logger.info(f"PDF adjunto preparado para SAP ({len(pdf_content)} bytes)")
                            else:
                                logger.warning(f"No se pudo obtener contenido del PDF {self.pdf_file.name}")
                        except Exception as e: 
                            logger.error(f"Error cargando PDF para SAP: {e}")

                    # 2. Las fotos de terreno
                    for att in self.attachments:
                        if att.file:
                            try:
                                att.file.open()
                                attachments.append({
                                    'name': f"Foto_{att.id}_{att.file.name.split('/')[-1]}",
                                    'content': base64.b64encode(att.file.read()).decode()
                                })
                                att.file.close()
                            except Exception as e: logger.error(f"Error cargando foto {att.id} para SAP: {e}")

                    res = sap_service.create_service_call(
                        customer_code=self.client_rut,
                        subject=f"Visita {self.report_number} - {self.project_name or self.client_name}",
                        description=self.general_observations or self.visit_reason or "Reporte de Visita Técnica",
                        technician_code=self.technician_id,
                        bp_project_code=self.project_id,
                        obra_name=self.project_name,
                        udf_data=udf,
                        report_id=self.report_number,
                        attachments=attachments
                    )
                    
                    if res and res.get('success'):
                        self.sap_call_id = res.get('id') # El servicio devuelve 'id' (ServiceCallID)
                        self.sap_doc_num = res.get('doc_num')
                        self.sync_status = 'synced'
                        self.last_synced_at = timezone.now()
                    else:
                        self.sync_status = 'error'
                        self.sync_error_message = res.get('error') if res else "Error desconocido en SAP"
                else:
                    # CASO B: Actualizar Llamada existente
                    logger.info(f"Actualizando Llamada de Servicio SAP {self.sap_call_id}")
                    # Sincronización básica de estado para llamadas existentes
                    self.sync_status = 'synced'
                    self.last_synced_at = timezone.now()
                    
                    # Si el DocNum se perdió en el objeto pero existe en DB, recuperarlo
                    if not self.sap_doc_num:
                        # Esto ayuda si el frontend no envió el doc_num pero sí el call_id
                        try:
                            from apps.sap_integration.sap_query_service import SAPQueryService
                            sc_data = SAPQueryService().get_service_call_by_id(self.sap_call_id)
                            if sc_data:
                                self.sap_doc_num = sc_data.get('doc_num')
                        except: pass
                
                # CASO B-1: Si el estado es CLOSED y ya tenemos la llamada SAP, la cerramos
                if self.status == VisitStatus.CLOSED and self.sap_call_id:
                    logger.info(f"Cerrando Llamada de Servicio SAP {self.sap_call_id} por estado CLOSED")
                    res_text = f"Visita realizada. Reporte N°: {self.report_number}. Reporte firmado elaborado por: {self.technician or 'Técnico'}."
                    close_res = sap_service.close_service_call(self.sap_call_id, res_text)
                    if close_res and close_res.get('success'):
                        logger.info(f"Llamada SAP {self.sap_call_id} cerrada exitosamente.")
                        self.sync_status = 'synced'
                        self.last_synced_at = timezone.now()
                        self.sync_error_message = ""
                    else:
                        logger.warning(f"Error al cerrar llamada SAP {self.sap_call_id}: {close_res.get('error')}")
                        self.sync_status = 'error'
                        self.sync_error_message = close_res.get('error') or "Error al cerrar llamada en SAP"

                # Guardar estado de sincronización sin disparar recursividad
                VisitReport.objects.filter(pk=self.pk).update(
                    sap_call_id=self.sap_call_id,
                    sap_doc_num=self.sap_doc_num,
                    sync_status=self.sync_status,
                    last_synced_at=self.last_synced_at,
                    sync_error_message=self.sync_error_message
                )

                # CASO C: Sincronización del PDF Firmado (Anexo Final)
                # Si ya tenemos la llamada de SAP pero el PDF se generó después (típico en flujo de firma)
                if self.sap_call_id and self.pdf_file:
                    try:
                        import os
                        
                        pdf_path = None
                        try:
                            pdf_path = self.pdf_file.path
                        except:
                            # Fallback si storage no soporta .path
                            pass

                        pdf_content = None
                        if pdf_path and os.path.exists(pdf_path):
                            with open(pdf_path, 'rb') as f:
                                pdf_content = f.read()
                        else:
                            # Leer desde storage
                            self.pdf_file.open('rb')
                            pdf_content = self.pdf_file.read()
                            self.pdf_file.close()

                        if pdf_content:
                            files = [{
                                'name': f"Reporte_{self.report_number}_Firmado.pdf",
                                'content': base64.b64encode(pdf_content).decode()
                            }]
                            
                            logger.info(f"Subiendo PDF firmado de {self.report_number} a SAP (CallID: {self.sap_call_id})")
                            res = sap_service.update_service_call_attachment(self.sap_call_id, files)
                            if res.get('success'):
                                logger.info(f"PDF firmado sincronizado exitosamente con SAP (AtcEntry: {res.get('atc_entry')})")
                            else:
                                logger.warning(f"Error al subir PDF a SAP: {res.get('error')}")
                    except Exception as pdf_err:
                        logger.error(f"Error procesando PDF para SAP: {pdf_err}")

        except Exception as e:
            logger.error(f"ERROR CRÍTICO en VisitReport.save: {str(e)}\n{traceback.format_exc()}")
            raise e

    @property
    def attachments(self):
        """Devuelve los adjuntos relacionados a este reporte"""
        try:
            from django.apps import apps
            DocumentAttachment = apps.get_model('documents', 'DocumentAttachment')
            return DocumentAttachment.objects.filter(document_type='visit_report', document_id=self.id)
        except LookupError:
            return []
