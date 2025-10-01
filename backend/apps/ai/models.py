from django.db import models
from apps.users.models import User

class AIAnalysis(models.Model):
    """Model to store AI analysis results"""
    ANALYSIS_TYPES = [
        ('image_analysis', 'Análisis de Imagen'),
        ('document_analysis', 'Análisis de Documento'),
        ('technical_report', 'Informe Técnico'),
        ('quality_inspection', 'Inspección de Calidad'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_analyses')
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input data
    input_file_path = models.CharField(max_length=500, blank=True, null=True)
    input_description = models.TextField(blank=True, null=True)
    
    # AI Provider info
    ai_provider = models.CharField(max_length=100, default='openai')
    model_used = models.CharField(max_length=100, default='gpt-4o')
    
    # Results
    raw_response = models.JSONField(blank=True, null=True)
    processed_analysis = models.TextField(blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    
    # Generated content
    generated_report = models.TextField(blank=True, null=True)
    report_file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Metadata
    processing_time = models.FloatField(blank=True, null=True)  # in seconds
    tokens_used = models.IntegerField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Análisis de IA'
        verbose_name_plural = 'Análisis de IA'
    
    def __str__(self):
        return f"Análisis {self.get_analysis_type_display()} - {self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

class AIProvider(models.Model):
    """Model to store AI provider configurations"""
    name = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=500)
    base_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)
    
    # Rate limiting
    requests_per_minute = models.IntegerField(default=60)
    requests_per_day = models.IntegerField(default=1000)
    
    # Cost tracking
    cost_per_token = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'name']
        verbose_name = 'Proveedor de IA'
        verbose_name_plural = 'Proveedores de IA'
    
    def __str__(self):
        return f"{self.name} ({'Activo' if self.is_active else 'Inactivo'})"
