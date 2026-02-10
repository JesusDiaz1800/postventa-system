from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User


class Category(models.Model):
    """Model for product categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']


class Responsible(models.Model):
    """Model for responsible technicians"""
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Responsable'
        verbose_name_plural = 'Responsables'
        ordering = ['name']


class Incident(models.Model):
    """
    Model for post-sales incidents
    """
    STATUS_CHOICES = [
        ('abierto', 'Abierto'),
        ('reporte_visita', 'En Reporte de Visita'),
        ('calidad', 'En Calidad'),
        ('proveedor', 'En Proveedor'),
        ('cerrado', 'Cerrado'),
    ]
    
    # Etapa en la que se cerró la incidencia
    STAGE_CLOSED_CHOICES = [
        ('incidencia', 'Cerrada en Incidencia'),
        ('reporte_visita', 'Cerrada en Reporte de Visita'),
        ('calidad', 'Cerrada en Calidad'),
        ('proveedor', 'Cerrada en Proveedor'),
    ]
    
    PRIORITY_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]

    
    # Basic incident information
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Código único de la incidencia (ej. INC-2025-0001)'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_incidents',
        help_text='Usuario que creó la incidencia'
    )
    
    # Client and project information
    provider = models.CharField(
        max_length=200,
        help_text='Proveedor del producto'
    )
    
    obra = models.CharField(
        max_length=200,
        help_text='Obra o proyecto'
    )
    
    cliente = models.CharField(
        max_length=200,
        help_text='Nombre del cliente'
    )
    
    cliente_rut = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        default='',
        help_text='RUT del cliente'
    )
    
    direccion_cliente = models.TextField(
        blank=True,
        help_text='Dirección del cliente'
    )

    # SAP Integration Fields
    customer_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='',
        help_text='Código del cliente en SAP (CardCode)'
    )

    project_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='',
        help_text='Código del proyecto en SAP (BPProjCode)'
    )

    salesperson = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text='Vendedor asignado (U_NX_VENDEDOR)'
    )

    sap_call_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text='ID de Llamada de Servicio en SAP'
    )
    
    # Product information
    sku = models.CharField(
        max_length=100,
        default='N/A',
        help_text='SKU del producto'
    )
    
    lote = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text='Número de lote'
    )
    
    factura_num = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text='Número de factura'
    )
    
    pedido_num = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text='Número de pedido'
    )
    
    # Incident details
    fecha_reporte = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora del reporte'
    )
    
    fecha_deteccion = models.DateField(
        help_text='Fecha de detección del problema'
    )
    
    hora_deteccion = models.TimeField(
        help_text='Hora de detección del problema'
    )
    
    descripcion = models.TextField(
        help_text='Descripción detallada del problema'
    )
    
    acciones_inmediatas = models.TextField(
        blank=True,
        null=True,
        default='',
        help_text='Acciones inmediatas adoptadas'
    )
    
    # Classification
    categoria = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Categoría del producto'
    )
    
    subcategoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text='Subcategoría específica'
    )
    
    prioridad = models.CharField(
        max_length=20,
        # Basic incident information
        # ADVERTENCIA: Revisa los tipos de datos y relaciones para compatibilidad total con SQL Server. Evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
        default='media',
        help_text='Prioridad de la incidencia'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='abierto',
        help_text='Estado actual de la incidencia'
    )
    
    # Assignment and tracking
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        help_text='Usuario asignado para resolver la incidencia'
    )
    
    # Responsable del área técnica
    responsable = models.ForeignKey(
        Responsible,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Responsable técnico asignado'
    )
    
    # Campos de escalamiento
    escalated_to_quality = models.BooleanField(
        default=False,
        help_text='Indica si la incidencia fue escalada a calidad'
    )
    
    escalated_to_supplier = models.BooleanField(
        default=False,
        help_text='Indica si la incidencia fue escalada a proveedor'
    )
    
    escalated_to_internal_quality = models.BooleanField(
        default=False,
        help_text='Indica si la incidencia fue escalada a calidad interna'
    )

    escalation_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de escalamiento'
    )
    
    escalation_reason = models.TextField(
        blank=True,
        help_text='Razón del escalamiento'
    )
    
    # Registro de evolución/acciones posteriores (del PDF)
    acciones_posteriores = models.TextField(
        blank=True,
        help_text='Registro de evolución/acciones posteriores'
    )
    
    # Referencias NC/NP del PDF
    nc_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text='Número de nota de crédito'
    )
    
    np_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text='Número de nota de pedido'
    )
    
    # Análisis de IA
    ai_analysis = models.JSONField(
        null=True,
        blank=True,
        help_text='Análisis realizado por IA'
    )
    
    ai_analysis_accuracy = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Precisión del análisis de IA (0-1)'
    )
    
    # Fecha de cierre específica
    fecha_cierre = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de cierre de la incidencia'
    )
    
    # Closure information
    closed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_incidents',
        help_text='Usuario que cerró la incidencia'
    )
    
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha y hora de cierre'
    )
    
    # Etapa en la que se cerró la incidencia
    closed_at_stage = models.CharField(
        max_length=20,
        choices=STAGE_CLOSED_CHOICES,
        null=True,
        blank=True,
        help_text='Etapa del workflow en la que se cerró la incidencia'
    )
    
    # Campos de cierre obligatorio
    closure_summary = models.TextField(
        blank=True,
        help_text='Resumen obligatorio de acciones, conclusiones y decisiones tomadas al cerrar la incidencia'
    )
    
    closure_attachment = models.CharField(
        max_length=500,
        blank=True,
        help_text='Ruta del archivo adjunto con información de cierre'
    )
    
    # SLA y métricas de tiempo
    sla_due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha límite según SLA'
    )
    
    sla_breached = models.BooleanField(
        default=False,
        help_text='Indica si se incumplió el SLA'
    )
    
    first_response_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha/hora de primera respuesta'
    )
    
    resolution_time_hours = models.FloatField(
        null=True,
        blank=True,
        help_text='Tiempo total de resolución en horas'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'incidents'
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['created_at', 'estado']),
            models.Index(fields=['cliente_rut']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.cliente} ({self.estado})"
    
    def save(self, *args, **kwargs):
        # ==================== NUCLEAR INTEGRITY SHIELD ====================
        # Garantizar que campos de texto opcionales NUNCA sean NULL para SQL Server
        # Esta es la última línea de defensa contra IntegrityError en entornos donde
        # las migraciones no actualizan correctamente las restricciones NOT NULL.
        # Ejecuta SIEMPRE, independientemente de señales o configuración externa.
        text_fields_to_sanitize = [
            'subcategoria', 'cliente_rut', 'customer_code', 'project_code', 
            'salesperson', 'lote', 'factura_num', 'pedido_num', 
            'acciones_inmediatas', 'nc_number', 'np_number'
        ]
        for field_name in text_fields_to_sanitize:
            current_value = getattr(self, field_name, None)
            if current_value is None:
                setattr(self, field_name, '')
        # ==================================================================
        
        if not self.code:
            self.code = self.generate_code()
        if not self.fecha_reporte:
            self.fecha_reporte = timezone.now()
        super().save(*args, **kwargs)
    
    def generate_code(self):
        """Generate unique incident code based on detection year"""
        year = self.fecha_deteccion.year if self.fecha_deteccion else timezone.now().year
        
        # Find the highest number for this year
        incidents_this_year = Incident.objects.filter(
            code__startswith=f'INC-{year}'
        ).values_list('code', flat=True)
        
        max_number = 0
        for code in incidents_this_year:
            try:
                parts = code.split('-')
                # Format is usually INC-YYYY-NNNN (3 parts)
                if len(parts) >= 3:
                    number = int(parts[-1])
                    max_number = max(max_number, number)
            except (ValueError, IndexError):
                continue
        
        # Generate new code with retry logic for duplicates
        new_number = max_number + 1
        base_code = f'INC-{year}-{new_number:04d}'
        
        # Check if code already exists and increment if necessary
        while Incident.objects.filter(code=base_code).exists():
            new_number += 1
            base_code = f'INC-{year}-{new_number:04d}'
        
        return base_code
    
    def close(self, user, stage='incidencia', summary='', attachment_path=''):
        """
        Close the incident with required summary
        
        Args:
            user: User who is closing the incident
            stage: Stage where incident is being closed (incidencia, reporte_visita, calidad, proveedor)
            summary: Required closure summary (actions, conclusions, decisions)
            attachment_path: Optional path to closure attachment
        """
        self.estado = 'cerrado'
        self.closed_by = user
        self.closed_at = timezone.now()
        self.fecha_cierre = timezone.now().date()
        self.closed_at_stage = stage
        self.closure_summary = summary
        
        # --- LOGICA DE VINCULACIÓN INTELIGENTE DE ADJUNTOS ---
        final_attachment_path = attachment_path
        
        # 1. Si viene un path simple (solo nombre), intentar buscar en IncidentAttachment
        if final_attachment_path and '/' not in final_attachment_path and '\\' not in final_attachment_path:
            # Es probable que sea solo el nombre de archivo enviado desde el frontend
            # Buscar si existe un adjunto con ese nombre para esta incidencia
            from .models import IncidentAttachment # Import local to avoid circular dep if any
            matching_attachment = self.attachments.filter(file_name=final_attachment_path).first()
            if matching_attachment:
                final_attachment_path = matching_attachment.file_path
        
        # 2. Si NO viene adjunto, intentar autovincular el último reporte generado
        if not final_attachment_path:
            # Prioridad 1: Reporte de Visita (si se cierra en esa etapa o tiene uno reciente)
            if hasattr(self, 'documents_visit_reports'): # Reverse relation check
                last_visit_report = self.documents_visit_reports.exclude(pdf_file='').order_by('-created_at').first()
                if last_visit_report and last_visit_report.pdf_file:
                    final_attachment_path = last_visit_report.pdf_file.name
            
            # Prioridad 2: Si no hubo visita, quizás Lab Report (si aplica, aunque LabReport model actual usa expert_signature_path, no tiene pdf_file explicito aqui, revistar modelo)
            # El modelo LabReport mostrado anteriormente no tenia 'pdf_file', asi que omitimos o verificamos.
            # (Revisando modelo LabReport: no tiene pdf_file standard en lo que vi, pero si QualityReport en documents app).
            
            if not final_attachment_path:
                 # Intentar buscar QualityReport (interno o cliente)
                 try:
                     from apps.documents.models import QualityReport
                     last_quality_report = QualityReport.objects.filter(related_incident=self).exclude(pdf_path__isnull=True).order_by('-created_at').first()
                     if last_quality_report and last_quality_report.pdf_path:
                         final_attachment_path = last_quality_report.pdf_path
                 except (ImportError, Exception):
                     pass

        self.closure_attachment = final_attachment_path
        
        # Calcular tiempo de resolución en horas
        if self.created_at:
            delta = timezone.now() - self.created_at
            self.resolution_time_hours = round(delta.total_seconds() / 3600, 2)
        
        # Verificar si se incumplió el SLA
        if self.sla_due_date and timezone.now() > self.sla_due_date:
            self.sla_breached = True
        
        self.save()
    
    def get_photos_list(self):
        """Obtiene lista de fotos anexas para documentos"""
        photos = self.images.all()
        if photos:
            return "\n".join([f"- {photo.filename}: {photo.caption_ai or 'Sin descripción'}" for photo in photos])
        return "No hay fotos anexas"


class IncidentImage(models.Model):
    """
    Model for incident images with AI analysis
    """
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='images',
        help_text='Incidencia relacionada'
    )
    
    filename = models.CharField(
        max_length=255,
        help_text='Nombre del archivo'
    )
    
    path = models.CharField(
        max_length=500,
        help_text='Ruta del archivo en el storage'
    )
    
    file_size = models.BigIntegerField(
        help_text='Tamaño del archivo en bytes'
    )
    
    mime_type = models.CharField(
        max_length=100,
        help_text='Tipo MIME del archivo'
    )
    
    # EXIF data
    exif_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='Datos EXIF de la imagen'
    )
    
    # AI Analysis
    caption_ai = models.TextField(
        blank=True,
        help_text='Descripción generada por IA'
    )
    
    analysis_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='Análisis completo de IA (causas sugeridas, confianza, etc.)'
    )
    
    ai_provider_used = models.CharField(
        max_length=50,
        blank=True,
        help_text='Proveedor de IA utilizado para el análisis'
    )
    
    ai_confidence = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Nivel de confianza del análisis de IA (0-1)'
    )
    
    # Metadata
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que subió la imagen'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'incident_images'
        verbose_name = 'Imagen de Incidencia'
        verbose_name_plural = 'Imágenes de Incidencias'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.incident.code} - {self.filename}"


class LabReport(models.Model):
    """
    Model for laboratory reports
    """
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='lab_reports',
        help_text='Incidencia relacionada'
    )
    
    sample_description = models.TextField(
        help_text='Descripción de la muestra enviada'
    )
    
    tests_performed = models.JSONField(
        default=list,
        help_text='Lista de ensayos realizados'
    )
    
    observations = models.TextField(
        help_text='Observaciones del laboratorio'
    )
    
    conclusions = models.TextField(
        help_text='Conclusiones técnicas del laboratorio'
    )
    
    expert_name = models.CharField(
        max_length=200,
        help_text='Nombre del experto que realizó el análisis'
    )
    
    expert_signature_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='Ruta de la firma del experto'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que creó el reporte'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lab_reports'
        verbose_name = 'Reporte de Laboratorio'
        verbose_name_plural = 'Reportes de Laboratorio'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Lab Report - {self.incident.code}"


class IncidentTimeline(models.Model):
    """
    Model for incident timeline/activity log
    """
    ACTION_CHOICES = [
        ('created', 'Creado'),
        ('updated', 'Actualizado'),
        ('assigned', 'Asignado'),
        ('status_changed', 'Estado Cambiado'),
        ('image_uploaded', 'Imagen Subida'),
        ('document_generated', 'Documento Generado'),
        ('lab_report_added', 'Reporte de Lab Agregado'),
        ('closed', 'Cerrado'),
        ('reopened', 'Reabierto'),
        ('deleted', 'Eliminado'),
    ]
    
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='timeline',
        help_text='Incidencia relacionada'
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text='Acción realizada'
    )
    
    description = models.TextField(
        help_text='Descripción de la acción'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que realizó la acción'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Metadatos adicionales de la acción'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'incident_timeline'
        verbose_name = 'Línea de Tiempo'
        verbose_name_plural = 'Líneas de Tiempo'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.incident.code} - {self.get_action_display()}"


class IncidentAttachment(models.Model):
    """
    Modelo para adjuntos de incidencias
    """
    ATTACHMENT_TYPE_CHOICES = [
        ('image', 'Imagen'),
        ('document', 'Documento'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Otro'),
    ]
    
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text='Incidencia a la que pertenece el adjunto'
    )
    
    file_name = models.CharField(
        max_length=255,
        help_text='Nombre del archivo'
    )
    
    file_path = models.CharField(
        max_length=500,
        help_text='Ruta del archivo en el sistema'
    )
    
    file_size = models.BigIntegerField(
        help_text='Tamaño del archivo en bytes'
    )
    
    file_type = models.CharField(
        max_length=50,
        choices=ATTACHMENT_TYPE_CHOICES,
        help_text='Tipo de archivo'
    )
    
    mime_type = models.CharField(
        max_length=100,
        help_text='Tipo MIME del archivo'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción del adjunto'
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_attachments',
        help_text='Usuario que subió el archivo'
    )
    
    uploaded_at = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora de subida'
    )
    
    is_public = models.BooleanField(
        default=True,
        help_text='Si el adjunto es público o privado'
    )
    
    class Meta:
        db_table = 'incident_attachments'
        verbose_name = 'Adjunto de Incidencia'
        verbose_name_plural = 'Adjuntos de Incidencias'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.incident.code} - {self.file_name}"
    
    @property
    def file_size_human(self):
        """Retorna el tamaño del archivo en formato legible"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
