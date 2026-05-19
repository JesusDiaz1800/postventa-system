"""
Serializers para reportes de calidad - OBSOLETO (Mantenido solo por compatibilidad de imports residuales)
"""
from rest_framework import serializers

class QualityReportSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {"error": "Este reporte ya no está disponible en SERTEC-SYSTEM"}

class QualityReportCreateSerializer(serializers.Serializer):
    pass

class QualityReportUpdateSerializer(serializers.Serializer):
    pass
