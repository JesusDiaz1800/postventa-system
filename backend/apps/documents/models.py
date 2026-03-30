"""
Modelos para gestión de documentos con trazabilidad completa
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.incidents.models import Incident
from apps.core.thread_local import get_current_country

User = get_user_model()

# ==================== MODELOS EXISTENTES ====================

class DocumentTemplate(models.Model):
    """
    Modelo para plantillas de documentos
    """
    name = models.CharField(max_length=200, help_text='Nombre de la plantilla')
    template_type = models.CharField(
        max_length=50,
        choices=[
            ('cliente_informe', 'Informe para Cliente'),
            ('proveedor_carta', 'Carta para Proveedor'),
            ('lab_report', 'Reporte de Laboratorio'),
            ('tecnico_informe', 'Informe Técnico')
        ],
        help_text='Tipo de plantilla'
    )
    description = models.TextField(blank=True, help_text='Descripción de la plantilla')
    docx_template_path = models.CharField(max_length=500, help_text='Ruta del archivo .docx de la plantilla')
    is_active = models.BooleanField(default=True, help_text='Indica si la plantilla está activa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que creó la plantilla'
    )
    
    class Meta:
        verbose_name = 'Plantilla de Documento'
        verbose_name_plural = 'Plantillas de Documentos'
        db_table = 'document_templates'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Document(models.Model):
    """
    Modelo para documentos generados
    """
    DOCUMENT_TYPE_CHOICES = [
        ('plantilla', 'Plantilla'),
        ('oficial', 'Documento Oficial'),
        ('borrador', 'Borrador'),
        ('incident_attachment', 'Adjunto de Incidencia'),
    ]
    
    title = models.CharField(max_length=200, help_text='Título del documento')
    filename = models.CharField(max_length=255, blank=True, help_text='Nombre del archivo')
    description = models.TextField(blank=True, help_text='Descripción del documento')
    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        default='oficial',
        help_text='Tipo de documento'
    )
    version = models.IntegerField(default=1, help_text='Versión del documento')
    docx_path = models.CharField(blank=True, max_length=500, help_text='Ruta del archivo .docx')
    pdf_path = models.CharField(blank=True, max_length=500, help_text='Ruta del archivo .pdf')
    file_path = models.CharField(blank=True, max_length=500, help_text='Ruta del archivo adjunto')
    size = models.BigIntegerField(default=0, help_text='Tamaño del archivo en bytes')
    content_html = models.TextField(blank=True, help_text='Contenido HTML del documento (para edición)')
    placeholders_data = models.JSONField(default=dict, help_text='Datos utilizados para reemplazar placeholders')
    notes = models.TextField(blank=True, help_text='Notas sobre el documento')
    is_final = models.BooleanField(default=False, help_text='Indica si es la versión final del documento')
    is_public = models.BooleanField(default=False, help_text='Indica si el documento es público')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que creó el documento'
    )
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True,
        help_text='Incidencia relacionada (opcional)'
    )
    
    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        db_table = 'documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

    def get_document_type_display(self):
        return dict(self.DOCUMENT_TYPE_CHOICES).get(self.document_type, self.document_type)

class DocumentVersion(models.Model):
    """
    Modelo para versiones de documentos
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField(help_text='Número de versión')
    docx_path = models.CharField(max_length=500, help_text='Ruta del archivo .docx de esta versión')
    pdf_path = models.CharField(blank=True, max_length=500, help_text='Ruta del archivo .pdf de esta versión')
    content_html = models.TextField(blank=True, help_text='Contenido HTML de esta versión')
    change_notes = models.TextField(blank=True, help_text='Notas sobre los cambios en esta versión')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que creó esta versión'
    )
    
    class Meta:
        verbose_name = 'Versión de Documento'
        verbose_name_plural = 'Versiones de Documentos'
        db_table = 'document_versions'
        ordering = ['-version_number']
        unique_together = ['document', 'version_number']
    
    def __str__(self):
        return f"{self.document.title} - Versión {self.version_number}"

class DocumentConversion(models.Model):
    """
    Modelo para conversiones de documentos
    """
    CONVERSION_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='conversions')
    source_format = models.CharField(max_length=10, help_text='Formato de origen')
    target_format = models.CharField(max_length=10, help_text='Formato de destino')
    status = models.CharField(
        max_length=20,
        choices=CONVERSION_STATUS_CHOICES,
        default='pending',
        help_text='Estado de la conversión'
    )
    source_file_path = models.CharField(max_length=500, default='', help_text='Ruta del archivo de origen')
    target_file_path = models.CharField(blank=True, max_length=500, default='', help_text='Ruta del archivo de destino')
    error_message = models.TextField(blank=True, help_text='Mensaje de error si la conversión falló')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que inició la conversión'
    )

    class Meta:
        verbose_name = 'Conversión de Documento'
        verbose_name_plural = 'Conversiones de Documentos'
        db_table = 'document_conversions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.document.title} - {self.source_format} a {self.target_format}"

def get_visit_report_pdf_path(instance, filename):
    """Genera ruta dinámica: <pais>/visit_reports/pdfs/YYYY/MM/filename"""
    country = get_current_country()
    year_month = timezone.now().strftime('%Y/%m')
    return f"{country}/visit_reports/pdfs/{year_month}/{filename}"

def get_attachment_upload_path(instance, filename):
    """Genera ruta dinámica: <pais>/documents/attachments/filename"""
    country = get_current_country()
    return f"{country}/documents/attachments/{filename}"

# ==================== NUEVOS MODELOS PARA TRAZABILIDAD ====================

class DocumentType(models.TextChoices):
    VISIT_REPORT = 'visit_report', 'Reporte de Visita'
    LAB_REPORT = 'lab_report', 'Informe de Laboratorio'
    SUPPLIER_REPORT = 'supplier_report', 'Informe para Proveedor'
    TECHNICAL_REPORT = 'technical_report', 'Informe Técnico'
    QUALITY_REPORT = 'quality_report', 'Informe de Calidad'

class DocumentStatus(models.TextChoices):
    DRAFT = 'draft', 'Borrador'
    PENDING_REVIEW = 'pending_review', 'Pendiente de Revisión'
    APPROVED = 'approved', 'Aprobado'
    SENT = 'sent', 'Enviado'
    WAITING_RESPONSE = 'waiting_response', 'Esperando Respuesta'
    CLOSED = 'closed', 'Cerrado'

class VisitReport(models.Model):
    """
    Modelo para reportes de visita técnica
    """
    # Información básica
    report_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Reporte")
    order_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Orden")
    visit_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Visita")
    
    # Vinculación con incidencia
    related_incident = models.ForeignKey(
        Incident, 
        on_delete=models.CASCADE,
        related_name='documents_visit_reports',
        verbose_name="Incidencia Relacionada"
    )
    
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
    technical_inspector = models.CharField(max_length=100, blank=True, verbose_name="Inspector Técnico de Obra")
    quality_manager = models.CharField(max_length=100, blank=True, verbose_name="Encargado de Calidad")
    management_manager = models.CharField(max_length=100, blank=True, verbose_name="Encargado de Gestión")
    
    # Datos de contacto adicionales
    fax = models.CharField(max_length=20, blank=True, verbose_name="Fax")
    contact_observations = models.TextField(blank=True, verbose_name="Observaciones de Contacto")
    
    # Ubicación
    commune = models.CharField(max_length=100, blank=True, null=True, verbose_name="Comuna")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    
    # Motivo de la visita
    visit_reason = models.CharField(max_length=100, blank=True, null=True, verbose_name="Motivo de la Visita")
    
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
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20, 
        choices=DocumentStatus.choices, 
        default=DocumentStatus.DRAFT,
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
    technician_signature = models.BooleanField(default=False, verbose_name="Firma del Técnico")
    installer_signature = models.BooleanField(default=False, verbose_name="Firma del Instalador")
    
    # Campos de almacenamiento
    docx_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ruta del documento DOCX")
    pdf_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ruta del documento PDF")

    
    # Integración SAP
    sap_call_id = models.IntegerField(null=True, blank=True, verbose_name="ID Llamada SAP", db_index=True)
    sync_status = models.CharField(max_length=20, default='pending', verbose_name="Estado Sincronización") # pending, synced, error
    last_synced_at = models.DateTimeField(null=True, blank=True, verbose_name="Última Sincronización")
    sync_error_message = models.TextField(blank=True, null=True, verbose_name="Error Sincronización")
    
    class Meta:
        verbose_name = "Reporte de Visita"
        verbose_name_plural = "Reportes de Visita"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reporte {self.report_number} - {self.project_name}"
    
    def save(self, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[MODEL] SAVE CALLED: self.report_number = '{self.report_number}'")
        
        # Solo generar report_number si no fue pre-asignado
        if not self.report_number:
            # Generar número SECUENCIAL PURO
            try:
                year = timezone.now().year
                
                last_report = VisitReport.objects.filter(
                    report_number__startswith=f"RV-{year}"
                ).exclude(id=self.id).order_by('-report_number').first()
                
                if last_report:
                    try:
                        last_number = int(last_report.report_number.split('-')[-1])
                        new_number = last_number + 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                
                self.report_number = f"RV-{year}-{new_number:03d}"
            except Exception as e:
                # Fallback si hay algún error
                import datetime
                self.report_number = f"RV-{timezone.now().year}-{timezone.now().strftime('%m%d%H%M')}"
        
        # Solo generar order_number si no existe
        if not self.order_number:
            # Usar el mismo formato que report_number para orden
            self.order_number = self.report_number
        
        super().save(*args, **kwargs)

    @property
    def attachments(self):
        """Devuelve los adjuntos relacionados a este reporte"""
        # Se usa globals() o import tardío porque DocumentAttachment se define más abajo
        try:
            # Intento seguro de obtener el modelo
            from django.apps import apps
            DocumentAttachment = apps.get_model('documents', 'DocumentAttachment')
            return DocumentAttachment.objects.filter(document_type='visit_report', document_id=self.id)
        except LookupError:
            return []

class LabReport(models.Model):
    """
    Modelo para informes de laboratorio
    """
    # Información básica
    report_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Informe")
    form_number = models.CharField(max_length=50, default="FORM-SERTEC-0007", verbose_name="Número de Formulario")
    request_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Solicitud")
    
    # Vinculación con incidencia y reporte de visita
    related_incident = models.ForeignKey(
        Incident, 
        on_delete=models.CASCADE,
        related_name='documents_lab_reports',
        verbose_name="Incidencia Relacionada"
    )
    related_visit_report = models.ForeignKey(
        VisitReport, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='lab_reports',
        verbose_name="Reporte de Visita Relacionado"
    )
    
    # Información del solicitante y cliente
    applicant = models.CharField(max_length=200, default="POLIFUSION", verbose_name="Solicitante")
    client = models.CharField(max_length=200, verbose_name="Cliente")
    
    # Descripción del problema
    description = models.TextField(verbose_name="Descripción")
    project_background = models.TextField(blank=True, verbose_name="Antecedentes del Proyecto")
    
    # Ensayos realizados
    tests_performed = models.JSONField(default=dict, verbose_name="Ensayos Realizados")
    
    # Comentarios y observaciones
    comments = models.TextField(blank=True, verbose_name="Comentarios")
    
    # Conclusiones
    conclusions = models.TextField(blank=True, verbose_name="Conclusiones")
    
    # Recomendaciones
    recommendations = models.TextField(blank=True, verbose_name="Recomendaciones")
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices, 
        default=DocumentStatus.DRAFT,
        verbose_name="Estado",
        db_index=True
    )
    
    # Metadatos
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_lab_reports',
        verbose_name="Creado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    # Firma del experto técnico
    technical_expert_signature = models.BooleanField(default=False, verbose_name="Firma del Experto Técnico")
    technical_expert_name = models.CharField(max_length=100, blank=True, verbose_name="Nombre del Experto Técnico")
    
    # Campos de almacenamiento
    docx_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ruta del documento DOCX")
    pdf_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ruta del documento PDF")
    
    class Meta:
        verbose_name = "Informe de Laboratorio"
        verbose_name_plural = "Informes de Laboratorio"
        ordering = ['-request_date']
    
    def __str__(self):
        return f"Informe {self.report_number} - {self.client}"
    
    def save(self, *args, **kwargs):
        if not self.report_number:
            # Generar número basado en el código de la incidencia: RP-YYYY-XXX
            # Ejemplo: INC-2025-0006 → RP-2025-006
            try:
                year = timezone.now().year
                
                # Extraer número secuencial de la incidencia relacionada
                if self.related_incident and self.related_incident.code:
                    incident_code = self.related_incident.code
                    parts = incident_code.split('-')
                    if len(parts) >= 3:
                        incident_seq = parts[-1].lstrip('0') or '1'
                        incident_number = int(incident_seq)
                    else:
                        incident_number = self.related_incident.id
                    
                    self.report_number = f"RP-{year}-{incident_number:03d}"
                else:
                    # Fallback si no hay incidencia relacionada
                    last_report = LabReport.objects.filter(
                        report_number__startswith=f"RP-{year}"
                    ).exclude(id=self.id).order_by('-report_number').first()
                    
                    if last_report:
                        try:
                            last_number = int(last_report.report_number.split('-')[-1])
                            new_number = last_number + 1
                        except (ValueError, IndexError):
                            new_number = 1
                    else:
                        new_number = 1
                    
                    self.report_number = f"RP-{year}-{new_number:03d}"
            except Exception as e:
                self.report_number = f"RP-{timezone.now().year}-{timezone.now().strftime('%m%d%H%M')}"
        super().save(*args, **kwargs)

class SupplierReport(models.Model):
    """
    Modelo para informes enviados a proveedores
    """
    # Información básica
    report_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Informe")
    report_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha del Informe")
    
    # Vinculación con incidencia y documentos relacionados
    related_incident = models.ForeignKey(
        Incident, 
        on_delete=models.CASCADE, 
        related_name='documents_supplier_reports',
        verbose_name="Incidencia Relacionada"
    )
    related_lab_report = models.ForeignKey(
        LabReport, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='supplier_reports',
        verbose_name="Informe de Laboratorio Relacionado"
    )
    
    # Información del proveedor
    supplier_name = models.CharField(max_length=200, verbose_name="Nombre del Proveedor")
    supplier_contact = models.CharField(max_length=200, blank=True, verbose_name="Contacto del Proveedor")
    supplier_email = models.EmailField(blank=True, verbose_name="Email del Proveedor")
    
    # Contenido del informe
    subject = models.CharField(max_length=300, verbose_name="Asunto")
    introduction = models.TextField(verbose_name="Introducción")
    problem_description = models.TextField(verbose_name="Descripción del Problema")
    technical_analysis = models.TextField(verbose_name="Análisis Técnico")
    recommendations = models.TextField(verbose_name="Recomendaciones")
    expected_improvements = models.TextField(verbose_name="Mejoras Esperadas")
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20, 
        choices=DocumentStatus.choices, 
        default=DocumentStatus.DRAFT,
        verbose_name="Estado",
        db_index=True
    )
    sent_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Envío")
    
    # Metadatos
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='created_supplier_reports',
        verbose_name="Creado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    # Campos de almacenamiento
    docx_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ruta del documento DOCX")
    pdf_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Ruta del documento PDF")
    
    class Meta:
        verbose_name = "Informe para Proveedor"
        verbose_name_plural = "Informes para Proveedores"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Informe Proveedor {self.report_number} - {self.supplier_name}"
    
    def save(self, *args, **kwargs):
        if not self.report_number:
            # Generar número basado en el código de la incidencia: RCP-YYYY-XXX
            # Ejemplo: INC-2025-0006 → RCP-2025-006
            try:
                year = timezone.now().year
                
                # Extraer número secuencial de la incidencia relacionada
                if self.related_incident and self.related_incident.code:
                    incident_code = self.related_incident.code
                    parts = incident_code.split('-')
                    if len(parts) >= 3:
                        incident_seq = parts[-1].lstrip('0') or '1'
                        incident_number = int(incident_seq)
                    else:
                        incident_number = self.related_incident.id
                    
                    self.report_number = f"RCP-{year}-{incident_number:03d}"
                else:
                    # Fallback si no hay incidencia relacionada
                    last_report = SupplierReport.objects.filter(
                        report_number__startswith=f"RCP-{year}"
                    ).exclude(id=self.id).order_by('-report_number').first()
                    
                    if last_report:
                        try:
                            last_number = int(last_report.report_number.split('-')[-1])
                            new_number = last_number + 1
                        except (ValueError, IndexError):
                            new_number = 1
                    else:
                        new_number = 1
                    
                    self.report_number = f"RCP-{year}-{new_number:03d}"
            except Exception as e:
                self.report_number = f"RCP-{timezone.now().year}-{timezone.now().strftime('%m%d%H%M')}"
        super().save(*args, **kwargs)

class DocumentAttachment(models.Model):
    """
    Modelo para archivos adjuntos de documentos
    """
    DOCUMENT_TYPES = [
        ('visit_report', 'Reporte de Visita'),
        ('lab_report', 'Informe de Laboratorio'),
        ('supplier_report', 'Informe para Proveedor'),
        ('supplier_response', 'Respuesta del Proveedor'),
        ('incident_attachment', 'Adjunto de Incidencia'),
        ('quality_report', 'Reporte de Calidad'),
    ]
    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name="Tipo de Documento")
    document_id = models.PositiveIntegerField(verbose_name="ID del Documento")
    
    file = models.FileField(upload_to=get_attachment_upload_path, verbose_name="Archivo")
    filename = models.CharField(max_length=255, verbose_name="Nombre del Archivo")
    file_type = models.CharField(max_length=50, verbose_name="Tipo de Archivo")
    file_size = models.PositiveIntegerField(verbose_name="Tamaño del Archivo")
    
    section = models.CharField(max_length=100, blank=True, null=True, verbose_name="Sección del Documento")
    description = models.CharField(max_length=300, blank=True, verbose_name="Descripción")
    
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Subido por"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    
    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.get_document_type_display()}"

class QualityReport(models.Model):
    """
    Modelo para reportes de calidad con dos tipos: cliente e interno
    """
    REPORT_TYPE_CHOICES = [
        ('cliente', 'Informe para Cliente'),
        ('interno', 'Informe Interno de la Incidencia'),
    ]
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        help_text='Tipo de informe de calidad'
    )
    report_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Número único del reporte'
    )
    related_incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='quality_reports',
        help_text='Incidencia relacionada'
    )
    
    # Información general
    title = models.CharField(max_length=200, help_text='Título del informe')
    date_created = models.DateTimeField(default=timezone.now, help_text='Fecha de creación')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_quality_reports',
        help_text='Usuario que creó el reporte'
    )
    
    # Contenido del informe
    executive_summary = models.TextField(help_text='Resumen ejecutivo')
    problem_description = models.TextField(help_text='Descripción del problema')
    root_cause_analysis = models.TextField(help_text='Análisis de causa raíz')
    corrective_actions = models.TextField(help_text='Acciones correctivas implementadas')
    preventive_measures = models.TextField(help_text='Medidas preventivas')
    recommendations = models.TextField(help_text='Recomendaciones')
    
    # Información técnica (más detallada para informe interno)
    technical_details = models.TextField(
        blank=True,
        help_text='Detalles técnicos específicos (principalmente para informe interno)'
    )
    internal_notes = models.TextField(
        blank=True,
        help_text='Notas internas (solo para informe interno)'
    )
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Borrador'),
            ('review', 'En Revisión'),
            ('approved', 'Aprobado'),
            ('sent', 'Enviado'),
            ('escalated', 'Escalado'),
            ('closed', 'Cerrado')
        ],
        default='draft',
        help_text='Estado del reporte',
        db_index=True
    )
    
    # Archivos generados
    pdf_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='Ruta del archivo PDF generado'
    )
    docx_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='Ruta del archivo DOCX generado'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reporte de Calidad'
        verbose_name_plural = 'Reportes de Calidad'
        db_table = 'quality_reports'
        ordering = ['-created_at']
        unique_together = ['related_incident', 'report_type']
    
    def save(self, *args, **kwargs):
        if not self.report_number:
            # Generar número basado en el código de la incidencia:
            # RCC-YYYY-XXX para cliente (Reporte Calidad Cliente)
            # RCI-YYYY-XXX para interno (Reporte Calidad Interno)
            # Ejemplo: INC-2025-0006 → RCC-2025-006 o RCI-2025-006
            from datetime import datetime
            year = datetime.now().year
            prefix = 'RCC' if self.report_type == 'cliente' else 'RCI'
            
            # Extraer número secuencial de la incidencia relacionada
            if self.related_incident and self.related_incident.code:
                incident_code = self.related_incident.code
                parts = incident_code.split('-')
                if len(parts) >= 3:
                    incident_seq = parts[-1].lstrip('0') or '1'
                    incident_number = int(incident_seq)
                else:
                    incident_number = self.related_incident.id
                
                self.report_number = f"{prefix}-{year}-{incident_number:03d}"
            else:
                # Fallback si no hay incidencia relacionada
                last_report = QualityReport.objects.filter(
                    report_number__startswith=f"{prefix}-{year}"
                ).order_by('-report_number').first()
                
                if last_report:
                    try:
                        last_number = int(last_report.report_number.split('-')[-1])
                        new_number = last_number + 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                
                self.report_number = f"{prefix}-{year}-{new_number:03d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Quality Report {self.report_number} - {self.get_report_type_display()} - {self.related_incident.code if self.related_incident else 'No Incident'}"