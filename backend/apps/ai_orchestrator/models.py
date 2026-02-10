from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class AIProvider(models.Model):
    """
    Model for AI provider configuration and quota management
    """
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google Gemini'),
        ('local', 'Modelo Local'),
    ]
    
    name = models.CharField(
        max_length=50,
        choices=PROVIDER_CHOICES,
        unique=True,
        help_text='Nombre del proveedor de IA'
    )
    
    api_key_encrypted = models.TextField(
        blank=True,
        help_text='API Key encriptada'
    )
    
    enabled = models.BooleanField(
        default=True,
        help_text='Indica si el proveedor está habilitado'
    )
    
    priority = models.IntegerField(
        default=1,
        help_text='Prioridad del proveedor (menor número = mayor prioridad)'
    )
    
    # Quota management
    daily_quota_tokens = models.IntegerField(
        default=100000,
        help_text='Cuota diaria de tokens'
    )
    
    daily_quota_calls = models.IntegerField(
        default=1000,
        help_text='Cuota diaria de llamadas'
    )
    
    quota_reset_time = models.TimeField(
        default='00:00',
        help_text='Hora de reinicio de cuota (formato HH:MM)'
    )
    
    # Usage tracking
    tokens_used_today = models.IntegerField(
        default=0,
        help_text='Tokens utilizados hoy'
    )
    
    calls_made_today = models.IntegerField(
        default=0,
        help_text='Llamadas realizadas hoy'
    )
    
    last_reset_date = models.DateField(
        default=timezone.now,
        help_text='Última fecha de reinicio de cuota'
    )
    
    # Configuration
    allow_external_uploads = models.BooleanField(
        default=True,
        help_text='Permitir envío de datos a proveedores externos'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_providers'
        verbose_name = 'Proveedor de IA'
        verbose_name_plural = 'Proveedores de IA'
        ordering = ['priority']
    
    def __str__(self):
        return f"{self.get_name_display()} (Prioridad: {self.priority})"
    
    def has_quota(self):
        """Check if provider has available quota"""
        today = timezone.now().date()
        
        # Reset quota if it's a new day
        if self.last_reset_date < today:
            self.reset_quota()
        
        return (
            self.tokens_used_today < self.daily_quota_tokens and
            self.calls_made_today < self.daily_quota_calls
        )
    
    def reset_quota(self):
        """Reset daily quota"""
        self.tokens_used_today = 0
        self.calls_made_today = 0
        self.last_reset_date = timezone.now().date()
        self.save(update_fields=['tokens_used_today', 'calls_made_today', 'last_reset_date'])
    
    def consume_quota(self, tokens_used, calls_made=1):
        """Consume quota for API calls"""
        self.tokens_used_today += tokens_used
        self.calls_made_today += calls_made
        self.save(update_fields=['tokens_used_today', 'calls_made_today'])
    
    def get_api_key(self):
        """Retorna la API Key desencriptada"""
        from apps.core.security_utils import decrypt_value
        return decrypt_value(self.api_key_encrypted)

    def set_api_key(self, raw_key):
        """Encripta y guarda la API Key"""
        from apps.core.security_utils import encrypt_value
        self.api_key_encrypted = encrypt_value(raw_key)

    def get_next_reset_time(self):
        """Get next quota reset time"""
        today = timezone.now().date()
        reset_datetime = timezone.datetime.combine(today, self.quota_reset_time)
        reset_datetime = timezone.make_aware(reset_datetime)
        
        # If reset time has passed today, next reset is tomorrow
        if reset_datetime <= timezone.now():
            reset_datetime += timezone.timedelta(days=1)
        
        return reset_datetime


class AIAnalysis(models.Model):
    """
    Model for storing AI analysis results
    """
    ANALYSIS_TYPE_CHOICES = [
        ('image_caption', 'Descripción de Imagen'),
        ('image_analysis', 'Análisis de Imagen'),
        ('text_rewrite', 'Reescritura de Texto'),
        ('cause_suggestion', 'Sugerencia de Causas'),
    ]
    
    analysis_type = models.CharField(
        max_length=50,
        choices=ANALYSIS_TYPE_CHOICES,
        help_text='Tipo de análisis realizado'
    )
    
    provider_used = models.ForeignKey(
        AIProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Proveedor de IA utilizado'
    )
    
    input_data = models.JSONField(
        help_text='Datos de entrada para el análisis'
    )
    
    output_data = models.JSONField(
        help_text='Resultados del análisis'
    )
    
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Puntuación de confianza (0-1)'
    )
    
    tokens_used = models.IntegerField(
        default=0,
        help_text='Tokens utilizados en el análisis'
    )
    
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text='Tiempo de procesamiento en segundos'
    )
    
    error_message = models.TextField(
        blank=True,
        help_text='Mensaje de error si el análisis falló'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_analyses'
        verbose_name = 'Análisis de IA'
        verbose_name_plural = 'Análisis de IA'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.provider_used} ({self.created_at})"


class AIUsageLog(models.Model):
    """
    Model for logging AI usage for monitoring and billing
    """
    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.CASCADE,
        help_text='Proveedor de IA utilizado'
    )
    
    analysis_type = models.CharField(
        max_length=50,
        choices=AIAnalysis.ANALYSIS_TYPE_CHOICES,
        help_text='Tipo de análisis'
    )
    
    tokens_used = models.IntegerField(
        help_text='Tokens utilizados'
    )
    
    cost_estimate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Costo estimado en USD'
    )
    
    success = models.BooleanField(
        default=True,
        help_text='Indica si la operación fue exitosa'
    )
    
    error_message = models.TextField(
        blank=True,
        help_text='Mensaje de error si la operación falló'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_usage_logs'
        verbose_name = 'Log de Uso de IA'
        verbose_name_plural = 'Logs de Uso de IA'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider} - {self.get_analysis_type_display()} ({self.created_at})"
