from rest_framework import serializers
from .models import BusinessPartner, ServiceCall, Project

class BusinessPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPartner
        fields = '__all__'

class ServiceCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCall
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
