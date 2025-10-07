from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json
import requests
import logging

from .models import (
    ExternalSystem, IntegrationTemplate, IntegrationInstance, 
    IntegrationLog, WebhookEndpoint, WebhookLog
)
from .serializers import (
    ExternalSystemSerializer, IntegrationTemplateSerializer, IntegrationInstanceSerializer,
    IntegrationLogSerializer, WebhookEndpointSerializer, WebhookLogSerializer,
    IntegrationTestSerializer, IntegrationSyncSerializer, WebhookTestSerializer
)
from .services import IntegrationService, WebhookService

logger = logging.getLogger(__name__)


class ExternalSystemViewSet(viewsets.ModelViewSet):
    """ViewSet para ExternalSystem"""
    
    queryset = ExternalSystem.objects.all()
    serializer_class = ExternalSystemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        system_type = self.request.query_params.get('system_type')
        if system_type:
            queryset = queryset.filter(system_type=system_type)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Probar conexión al sistema externo"""
        system = self.get_object()
        serializer = IntegrationTestSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service = IntegrationService()
                result = service.test_connection(system, serializer.validated_data)
                
                return Response({
                    'success': True,
                    'message': 'Conexión exitosa',
                    'data': result
                })
            except Exception as e:
                logger.error(f"Error testing connection to {system.name}: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error de conexión: {str(e)}',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sync_data(self, request, pk=None):
        """Sincronizar datos con el sistema externo"""
        system = self.get_object()
        serializer = IntegrationSyncSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service = IntegrationService()
                result = service.sync_data(system, serializer.validated_data)
                
                return Response({
                    'success': True,
                    'message': 'Sincronización iniciada',
                    'data': result
                })
            except Exception as e:
                logger.error(f"Error syncing data with {system.name}: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error de sincronización: {str(e)}',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de sistemas externos"""
        queryset = self.get_queryset()
        
        stats = {
            'total_systems': queryset.count(),
            'active_systems': queryset.filter(is_active=True).count(),
            'inactive_systems': queryset.filter(is_active=False).count(),
            'by_type': {},
            'by_status': {},
        }
        
        # Estadísticas por tipo
        for system_type, _ in ExternalSystem.SYSTEM_TYPES:
            count = queryset.filter(system_type=system_type).count()
            if count > 0:
                stats['by_type'][system_type] = count
        
        # Estadísticas por estado
        for status_choice, _ in ExternalSystem.STATUS_CHOICES:
            count = queryset.filter(status=status_choice).count()
            if count > 0:
                stats['by_status'][status_choice] = count
        
        return Response(stats)


class IntegrationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet para IntegrationTemplate"""
    
    queryset = IntegrationTemplate.objects.all()
    serializer_class = IntegrationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        template_type = self.request.query_params.get('template_type')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        source_system = self.request.query_params.get('source_system')
        if source_system:
            queryset = queryset.filter(source_system_id=source_system)
        
        target_system = self.request.query_params.get('target_system')
        if target_system:
            queryset = queryset.filter(target_system_id=target_system)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Ejecutar plantilla de integración"""
        template = self.get_object()
        
        try:
            service = IntegrationService()
            instance = service.execute_template(template, request.data, request.user)
            
            return Response({
                'success': True,
                'message': 'Integración ejecutada exitosamente',
                'instance_id': instance.id
            })
        except Exception as e:
            logger.error(f"Error executing template {template.name}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error ejecutando integración: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Probar plantilla de integración"""
        template = self.get_object()
        
        try:
            service = IntegrationService()
            result = service.test_template(template, request.data)
            
            return Response({
                'success': True,
                'message': 'Prueba exitosa',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error testing template {template.name}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error en la prueba: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class IntegrationInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet para IntegrationInstance"""
    
    queryset = IntegrationInstance.objects.all()
    serializer_class = IntegrationInstanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        template = self.request.query_params.get('template')
        if template:
            queryset = queryset.filter(template_id=template)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        related_incident = self.request.query_params.get('related_incident')
        if related_incident:
            queryset = queryset.filter(related_incident_id=related_incident)
        
        related_document = self.request.query_params.get('related_document')
        if related_document:
            queryset = queryset.filter(related_document_id=related_document)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar instancia de integración"""
        instance = self.get_object()
        
        if instance.status in ['completed', 'cancelled', 'failed']:
            return Response({
                'success': False,
                'message': 'La instancia no puede ser cancelada en su estado actual'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = IntegrationService()
            service.cancel_instance(instance, request.user)
            
            return Response({
                'success': True,
                'message': 'Instancia cancelada exitosamente'
            })
        except Exception as e:
            logger.error(f"Error cancelling instance {instance.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error cancelando instancia: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Reintentar instancia de integración"""
        instance = self.get_object()
        
        if instance.status not in ['failed']:
            return Response({
                'success': False,
                'message': 'Solo se pueden reintentar instancias fallidas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = IntegrationService()
            new_instance = service.retry_instance(instance, request.user)
            
            return Response({
                'success': True,
                'message': 'Instancia reintentada exitosamente',
                'new_instance_id': new_instance.id
            })
        except Exception as e:
            logger.error(f"Error retrying instance {instance.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error reintentando instancia: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de instancias de integración"""
        queryset = self.get_queryset()
        
        # Filtros de fecha
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        stats = {
            'total_instances': queryset.count(),
            'by_status': {},
            'by_template': {},
            'success_rate': 0,
            'average_duration': 0,
        }
        
        # Estadísticas por estado
        for status_choice, _ in IntegrationInstance.STATUS_CHOICES:
            count = queryset.filter(status=status_choice).count()
            if count > 0:
                stats['by_status'][status_choice] = count
        
        # Estadísticas por plantilla
        template_stats = queryset.values('template__name').annotate(count=Count('id'))
        for item in template_stats:
            stats['by_template'][item['template__name']] = item['count']
        
        # Tasa de éxito
        completed = queryset.filter(status='completed').count()
        total = queryset.count()
        if total > 0:
            stats['success_rate'] = (completed / total) * 100
        
        return Response(stats)


class IntegrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para IntegrationLog"""
    
    queryset = IntegrationLog.objects.all()
    serializer_class = IntegrationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        instance = self.request.query_params.get('instance')
        if instance:
            queryset = queryset.filter(instance_id=instance)
        
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        step = self.request.query_params.get('step')
        if step:
            queryset = queryset.filter(step__icontains=step)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset.order_by('-timestamp')


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """ViewSet para WebhookEndpoint"""
    
    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        http_method = self.request.query_params.get('http_method')
        if http_method:
            queryset = queryset.filter(http_method=http_method)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(url_path__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Probar endpoint de webhook"""
        endpoint = self.get_object()
        serializer = WebhookTestSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service = WebhookService()
                result = service.test_endpoint(endpoint, serializer.validated_data)
                
                return Response({
                    'success': True,
                    'message': 'Webhook probado exitosamente',
                    'data': result
                })
            except Exception as e:
                logger.error(f"Error testing webhook {endpoint.name}: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error probando webhook: {str(e)}',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de webhooks"""
        queryset = self.get_queryset()
        
        stats = {
            'total_endpoints': queryset.count(),
            'active_endpoints': queryset.filter(is_active=True).count(),
            'inactive_endpoints': queryset.filter(is_active=False).count(),
            'by_method': {},
            'recent_activity': {},
        }
        
        # Estadísticas por método HTTP
        for method, _ in WebhookEndpoint.HTTP_METHODS:
            count = queryset.filter(http_method=method).count()
            if count > 0:
                stats['by_method'][method] = count
        
        # Actividad reciente (últimos 7 días)
        week_ago = timezone.now() - timedelta(days=7)
        recent_logs = WebhookLog.objects.filter(timestamp__gte=week_ago)
        
        stats['recent_activity'] = {
            'total_requests': recent_logs.count(),
            'successful_requests': recent_logs.filter(status='processed').count(),
            'failed_requests': recent_logs.filter(status='failed').count(),
            'by_endpoint': {}
        }
        
        # Actividad por endpoint
        endpoint_stats = recent_logs.values('endpoint__name').annotate(count=Count('id'))
        for item in endpoint_stats:
            stats['recent_activity']['by_endpoint'][item['endpoint__name']] = item['count']
        
        return Response(stats)


class WebhookLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para WebhookLog"""
    
    queryset = WebhookLog.objects.all()
    serializer_class = WebhookLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        endpoint = self.request.query_params.get('endpoint')
        if endpoint:
            queryset = queryset.filter(endpoint_id=endpoint)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        request_method = self.request.query_params.get('request_method')
        if request_method:
            queryset = queryset.filter(request_method=request_method)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset.order_by('-timestamp')
