from rest_framework import serializers
from .models import (
    ExternalSystem, IntegrationTemplate, IntegrationInstance, 
    IntegrationLog, WebhookEndpoint, WebhookLog
)
from django.contrib.auth.models import User


class ExternalSystemSerializer(serializers.ModelSerializer):
    """Serializer para ExternalSystem"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ExternalSystem
        fields = [
            'id', 'name', 'description', 'system_type', 'status',
            'endpoint_url', 'base_url', 'api_key', 'username', 'password', 'token',
            'timeout', 'retry_attempts', 'retry_delay',
            'headers', 'default_params', 'auth_type', 'auth_config',
            'verify_ssl', 'ssl_cert_path', 'ssl_key_path',
            'use_proxy', 'proxy_url', 'proxy_username', 'proxy_password',
            'is_active', 'created_by', 'created_by_username', 'created_by_full_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'token': {'write_only': True},
            'proxy_password': {'write_only': True},
        }
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None
    
    def create(self, validated_data):
        # Ocultar información sensible en la respuesta
        instance = super().create(validated_data)
        if instance.password:
            instance.password = "***"
        if instance.token:
            instance.token = "***"
        if instance.proxy_password:
            instance.proxy_password = "***"
        return instance
    
    def update(self, instance, validated_data):
        # Ocultar información sensible en la respuesta
        instance = super().update(instance, validated_data)
        if instance.password:
            instance.password = "***"
        if instance.token:
            instance.token = "***"
        if instance.proxy_password:
            instance.proxy_password = "***"
        return instance


class IntegrationTemplateSerializer(serializers.ModelSerializer):
    """Serializer para IntegrationTemplate"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    source_system_name = serializers.CharField(source='source_system.name', read_only=True)
    target_system_name = serializers.CharField(source='target_system.name', read_only=True)
    
    class Meta:
        model = IntegrationTemplate
        fields = [
            'id', 'name', 'description', 'template_type',
            'source_system', 'source_system_name', 'target_system', 'target_system_name',
            'field_mapping', 'data_transformation',
            'sync_frequency', 'sync_direction', 'conflict_resolution',
            'filter_conditions', 'sync_conditions',
            'error_handling', 'retry_config',
            'is_active', 'created_by', 'created_by_username', 'created_by_full_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None


class IntegrationInstanceSerializer(serializers.ModelSerializer):
    """Serializer para IntegrationInstance"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    started_by_username = serializers.CharField(source='started_by.username', read_only=True)
    completed_by_username = serializers.CharField(source='completed_by.username', read_only=True)
    related_incident_code = serializers.CharField(source='related_incident.code', read_only=True)
    related_document_title = serializers.CharField(source='related_document.title', read_only=True)
    related_user_username = serializers.CharField(source='related_user.username', read_only=True)
    
    class Meta:
        model = IntegrationInstance
        fields = [
            'id', 'template', 'template_name', 'status',
            'related_incident', 'related_incident_code',
            'related_document', 'related_document_title',
            'related_user', 'related_user_username',
            'input_data', 'output_data', 'error_data',
            'custom_config', 'metadata',
            'started_at', 'completed_at', 'scheduled_at',
            'started_by', 'started_by_username',
            'completed_by', 'completed_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer para IntegrationLog"""
    
    instance_template_name = serializers.CharField(source='instance.template.name', read_only=True)
    
    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'instance', 'instance_template_name', 'level', 'message', 'details',
            'step', 'duration', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer para WebhookEndpoint"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'name', 'description', 'url_path', 'http_method',
            'requires_auth', 'auth_token', 'validate_signature', 'signature_header', 'signature_secret',
            'auto_process', 'processing_script', 'filter_conditions',
            'is_active', 'created_by', 'created_by_username', 'created_by_full_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'auth_token': {'write_only': True},
            'signature_secret': {'write_only': True},
        }
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None
    
    def create(self, validated_data):
        # Ocultar información sensible en la respuesta
        instance = super().create(validated_data)
        if instance.auth_token:
            instance.auth_token = "***"
        if instance.signature_secret:
            instance.signature_secret = "***"
        return instance
    
    def update(self, instance, validated_data):
        # Ocultar información sensible en la respuesta
        instance = super().update(instance, validated_data)
        if instance.auth_token:
            instance.auth_token = "***"
        if instance.signature_secret:
            instance.signature_secret = "***"
        return instance


class WebhookLogSerializer(serializers.ModelSerializer):
    """Serializer para WebhookLog"""
    
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)
    
    class Meta:
        model = WebhookLog
        fields = [
            'id', 'endpoint', 'endpoint_name', 'status',
            'request_method', 'request_headers', 'request_body', 'request_ip',
            'response_status', 'response_headers', 'response_body',
            'processing_time', 'error_message', 'error_details',
            'timestamp'
        ]
        read_only_fields = ['timestamp']


class IntegrationTestSerializer(serializers.Serializer):
    """Serializer para testing de integraciones"""
    
    system_id = serializers.IntegerField()
    test_type = serializers.ChoiceField(choices=[
        ('connection', 'Conexión'),
        ('authentication', 'Autenticación'),
        ('api_call', 'Llamada API'),
        ('data_sync', 'Sincronización de Datos'),
    ])
    test_data = serializers.JSONField(default=dict, required=False)
    timeout = serializers.IntegerField(default=30, required=False)


class IntegrationSyncSerializer(serializers.Serializer):
    """Serializer para sincronización de datos"""
    
    template_id = serializers.IntegerField()
    sync_direction = serializers.ChoiceField(choices=[
        ('source_to_target', 'Origen a Destino'),
        ('target_to_source', 'Destino a Origen'),
        ('bidirectional', 'Bidireccional'),
    ])
    filter_conditions = serializers.JSONField(default=dict, required=False)
    force_sync = serializers.BooleanField(default=False, required=False)
    dry_run = serializers.BooleanField(default=False, required=False)


class WebhookTestSerializer(serializers.Serializer):
    """Serializer para testing de webhooks"""
    
    endpoint_id = serializers.IntegerField()
    test_data = serializers.JSONField(default=dict, required=False)
    test_headers = serializers.JSONField(default=dict, required=False)
    simulate_request = serializers.BooleanField(default=True, required=False)
