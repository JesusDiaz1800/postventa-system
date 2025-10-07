from rest_framework import serializers
from .models import (
    BackupJob, BackupInstance, RestoreJob, BackupSchedule, 
    BackupStorage, BackupLog, BackupPolicy
)
from django.contrib.auth.models import User


class BackupJobSerializer(serializers.ModelSerializer):
    """Serializer para BackupJob"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    instances_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupJob
        fields = [
            'id', 'name', 'description', 'backup_type', 'status',
            'source_paths', 'destination_path', 'compression_enabled', 'encryption_enabled',
            'include_patterns', 'exclude_patterns', 'max_file_size', 'min_file_age',
            'retention_days', 'max_backups', 'is_scheduled', 'schedule_cron', 'schedule_timezone',
            'notify_on_success', 'notify_on_failure', 'email_recipients',
            'created_by', 'created_by_username', 'created_by_full_name',
            'created_at', 'updated_at', 'instances_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'instances_count']
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None
    
    def get_instances_count(self, obj):
        return obj.instances.count()


class BackupInstanceSerializer(serializers.ModelSerializer):
    """Serializer para BackupInstance"""
    
    job_name = serializers.CharField(source='job.name', read_only=True)
    started_by_username = serializers.CharField(source='started_by.username', read_only=True)
    completed_by_username = serializers.CharField(source='completed_by.username', read_only=True)
    backup_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupInstance
        fields = [
            'id', 'job', 'job_name', 'status', 'backup_path', 'backup_url', 'backup_size', 
            'files_count', 'directories_count', 'compression_ratio', 'encryption_algorithm',
            'started_at', 'completed_at', 'duration', 'started_by', 'started_by_username',
            'completed_by', 'completed_by_username', 'error_message', 'error_details', 
            'log_file_path', 'metadata'
        ]
        read_only_fields = ['started_at', 'completed_at', 'duration']
    
    def get_backup_url(self, obj):
        if obj.backup_path and obj.status == 'completed':
            return f"/api/backup/instances/{obj.id}/download/"
        return None


class RestoreJobSerializer(serializers.ModelSerializer):
    """Serializer para RestoreJob"""
    
    backup_instance_job_name = serializers.CharField(source='backup_instance.job.name', read_only=True)
    started_by_username = serializers.CharField(source='started_by.username', read_only=True)
    completed_by_username = serializers.CharField(source='completed_by.username', read_only=True)
    
    class Meta:
        model = RestoreJob
        fields = [
            'id', 'name', 'description', 'status', 'backup_instance', 'backup_instance_job_name',
            'destination_path', 'overwrite_existing', 'include_patterns', 'exclude_patterns',
            'restore_permissions', 'restore_timestamps', 'started_at', 'completed_at', 'duration',
            'started_by', 'started_by_username', 'completed_by', 'completed_by_username',
            'error_message', 'error_details', 'log_file_path', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['started_at', 'completed_at', 'duration', 'created_at', 'updated_at']


class BackupScheduleSerializer(serializers.ModelSerializer):
    """Serializer para BackupSchedule"""
    
    job_name = serializers.CharField(source='job.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupSchedule
        fields = [
            'id', 'job', 'job_name', 'name', 'description', 'status',
            'cron_expression', 'timezone', 'auto_execute', 'max_retries', 'retry_delay',
            'notify_on_success', 'notify_on_failure', 'email_recipients',
            'last_executed', 'next_execution', 'created_at', 'updated_at',
            'created_by', 'created_by_username', 'created_by_full_name'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_executed', 'next_execution']
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None


class BackupStorageSerializer(serializers.ModelSerializer):
    """Serializer para BackupStorage"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupStorage
        fields = [
            'id', 'name', 'description', 'storage_type', 'host', 'port', 'username', 'password', 'path',
            'config', 'use_ssl', 'verify_ssl', 'use_proxy', 'proxy_host', 'proxy_port',
            'proxy_username', 'proxy_password', 'is_active', 'created_by', 'created_by_username',
            'created_by_full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
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
        if instance.proxy_password:
            instance.proxy_password = "***"
        return instance
    
    def update(self, instance, validated_data):
        # Ocultar información sensible en la respuesta
        instance = super().update(instance, validated_data)
        if instance.password:
            instance.password = "***"
        if instance.proxy_password:
            instance.proxy_password = "***"
        return instance


class BackupLogSerializer(serializers.ModelSerializer):
    """Serializer para BackupLog"""
    
    job_name = serializers.CharField(source='job.name', read_only=True)
    
    class Meta:
        model = BackupLog
        fields = [
            'id', 'job', 'job_name', 'instance', 'level', 'message', 'details',
            'step', 'duration', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class BackupPolicySerializer(serializers.ModelSerializer):
    """Serializer para BackupPolicy"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupPolicy
        fields = [
            'id', 'name', 'description', 'policy_type', 'config',
            'applies_to_jobs', 'applies_to_schedules', 'is_active', 'priority',
            'created_by', 'created_by_username', 'created_by_full_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None


class BackupExecutionSerializer(serializers.Serializer):
    """Serializer para ejecución de backup"""
    
    job_id = serializers.IntegerField()
    custom_config = serializers.JSONField(default=dict, required=False)
    notify_on_completion = serializers.BooleanField(default=True, required=False)


class RestoreExecutionSerializer(serializers.Serializer):
    """Serializer para ejecución de restauración"""
    
    backup_instance_id = serializers.IntegerField()
    destination_path = serializers.CharField(max_length=500)
    overwrite_existing = serializers.BooleanField(default=False, required=False)
    include_patterns = serializers.ListField(child=serializers.CharField(), required=False)
    exclude_patterns = serializers.ListField(child=serializers.CharField(), required=False)


class BackupTestSerializer(serializers.Serializer):
    """Serializer para testing de backup"""
    
    storage_id = serializers.IntegerField(required=False)
    test_type = serializers.ChoiceField(choices=[
        ('connection', 'Conexión'),
        ('write', 'Escritura'),
        ('read', 'Lectura'),
        ('delete', 'Eliminación'),
    ])
    test_data = serializers.JSONField(default=dict, required=False)


class BackupStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de backup"""
    
    total_jobs = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    total_instances = serializers.IntegerField()
    successful_instances = serializers.IntegerField()
    failed_instances = serializers.IntegerField()
    total_size = serializers.IntegerField()
    by_type = serializers.DictField()
    by_status = serializers.DictField()
    recent_activity = serializers.DictField()
    storage_usage = serializers.DictField()
