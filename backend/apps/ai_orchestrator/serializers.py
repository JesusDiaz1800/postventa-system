from rest_framework import serializers
from .models import AIProvider, AIAnalysis


class AIProviderSerializer(serializers.ModelSerializer):
    """Serializer for AI Provider model"""
    
    class Meta:
        model = AIProvider
        fields = [
            'id', 'name', 'enabled', 'priority', 'daily_quota_tokens',
            'daily_quota_calls', 'quota_reset_time', 'tokens_used_today',
            'calls_made_today', 'last_reset_date', 'allow_external_uploads',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tokens_used_today', 'calls_made_today', 'last_reset_date',
            'created_at', 'updated_at'
        ]


class AIProviderCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating AI providers"""
    api_key = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = AIProvider
        fields = [
            'name', 'api_key', 'enabled', 'priority', 'daily_quota_tokens',
            'daily_quota_calls', 'quota_reset_time', 'allow_external_uploads'
        ]
    
    def create(self, validated_data):
        api_key = validated_data.pop('api_key', '')
        if api_key:
            # TODO: Encrypt API key
            validated_data['api_key_encrypted'] = api_key
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        api_key = validated_data.pop('api_key', None)
        if api_key is not None:
            # TODO: Encrypt API key
            instance.api_key_encrypted = api_key
        return super().update(instance, validated_data)


class AIAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for AI Analysis model"""
    provider_used = AIProviderSerializer(read_only=True)
    
    class Meta:
        model = AIAnalysis
        fields = [
            'id', 'analysis_type', 'provider_used', 'input_data', 'output_data',
            'confidence_score', 'tokens_used', 'processing_time', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ImageAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for image analysis requests"""
    image = serializers.ImageField(required=True)
    context = serializers.JSONField(required=False, default=dict)


class TextGenerationRequestSerializer(serializers.Serializer):
    """Serializer for text generation requests"""
    prompt = serializers.CharField(required=True)
    context = serializers.JSONField(required=False, default=dict)
    analysis_type = serializers.ChoiceField(
        choices=AIAnalysis.ANALYSIS_TYPE_CHOICES,
        default='text_rewrite'
    )
