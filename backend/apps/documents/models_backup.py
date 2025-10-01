"""
Modelos existentes para gestión de documentos
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.incidents.models import Incident

User = get_user_model()

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
    ]

    title = models.CharField(max_length=200, help_text='Título del documento')
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='oficial',
        help_text='Tipo de documento'
    )
    version = models.IntegerField(default=1, help_text='Versión del documento')
    docx_path = models.CharField(blank=True, max_length=500, help_text='Ruta del archivo .docx')
    pdf_path = models.CharField(blank=True, max_length=500, help_text='Ruta del archivo .pdf')
    content_html = models.TextField(blank=True, help_text='Contenido HTML del documento (para edición)')
    placeholders_data = models.JSONField(default=dict, help_text='Datos utilizados para reemplazar placeholders')
    notes = models.TextField(blank=True, help_text='Notas sobre el documento')
    is_final = models.BooleanField(default=False, help_text='Indica si es la versión final del documento')
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
    source_file_path = models.CharField(max_length=500, help_text='Ruta del archivo de origen')
    target_file_path = models.CharField(blank=True, max_length=500, help_text='Ruta del archivo de destino')
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
