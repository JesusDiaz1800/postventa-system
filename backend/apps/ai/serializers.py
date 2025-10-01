from rest_framework import serializers
from .models import AIAnalysis, AIProvider
from apps.users.serializers import UserSerializer

class AIProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIProvider
        fields = ['id', 'name', 'is_active', 'priority', 'requests_per_minute', 'requests_per_day', 'cost_per_token']
        read_only_fields = ['id']

class AIAnalysisSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    analysis_type_display = serializers.CharField(source='get_analysis_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AIAnalysis
        fields = [
            'id', 'user', 'analysis_type', 'analysis_type_display', 'status', 'status_display',
            'input_file_path', 'input_description', 'ai_provider', 'model_used',
            'processed_analysis', 'confidence_score', 'generated_report', 'report_file_path',
            'processing_time', 'tokens_used', 'cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class AIAnalysisCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysis
        fields = ['analysis_type', 'input_description']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
