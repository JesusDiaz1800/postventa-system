from rest_framework import serializers
from .models import VisitReport, VisitStatus
from django.contrib.auth import get_user_model

User = get_user_model()

class VisitReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    attachments = serializers.SerializerMethodField()
    
    class Meta:
        model = VisitReport
        fields = '__all__'
        read_only_fields = ('report_number', 'order_number', 'sap_call_id', 'sap_doc_num', 'sync_status', 'last_synced_at', 'sync_error_message', 'created_at', 'updated_at', 'created_by')

    def get_attachments(self, obj):
        from apps.documents.serializers import DocumentAttachmentSerializer
        attachments = obj.attachments
        return DocumentAttachmentSerializer(attachments, many=True).data


    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        # Manejar flag de finalización desde el frontend
        is_final = self.context['request'].data.get('is_final', False)
        if is_final:
            validated_data['status'] = VisitStatus.APPROVED
            
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Manejar flag de finalización desde el frontend en actualizaciones
        is_final = self.context['request'].data.get('is_final', False)
        if is_final:
            validated_data['status'] = VisitStatus.APPROVED
            
        return super().update(instance, validated_data)
