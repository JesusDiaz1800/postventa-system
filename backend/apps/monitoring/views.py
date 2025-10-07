from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    MonitoringRule, Alert, MetricValue, HealthCheck, HealthCheckResult,
    SystemMetrics, NotificationChannel, AlertTemplate, MonitoringDashboard,
    MonitoringWidget
)
from .serializers import (
    MonitoringRuleSerializer, MonitoringRuleCreateSerializer,
    AlertSerializer, AlertCreateSerializer, AlertUpdateSerializer,
    MetricValueSerializer, MetricValueCreateSerializer,
    HealthCheckSerializer, HealthCheckCreateSerializer,
    HealthCheckResultSerializer, HealthCheckResultCreateSerializer,
    SystemMetricsSerializer, SystemMetricsCreateSerializer,
    NotificationChannelSerializer, NotificationChannelCreateSerializer,
    NotificationChannelTestSerializer,
    AlertTemplateSerializer, AlertTemplateCreateSerializer,
    MonitoringDashboardSerializer, MonitoringDashboardCreateSerializer,
    MonitoringWidgetSerializer, MonitoringWidgetCreateSerializer,
    MonitoringStatisticsSerializer, MonitoringExecutionSerializer,
    MonitoringTestSerializer
)
from .services import MonitoringService, AlertService, HealthCheckService

logger = logging.getLogger(__name__)


class MonitoringRuleViewSet(viewsets.ModelViewSet):
    """ViewSet para MonitoringRule"""
    
    queryset = MonitoringRule.objects.all()
    serializer_class = MonitoringRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MonitoringRuleCreateSerializer
        return MonitoringRuleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        metric_type = self.request.query_params.get('metric_type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(metric_name__icontains=search)
            )
        
        return queryset.order_by('-severity', 'name')
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Probar regla de monitoreo"""
        rule = self.get_object()
        
        try:
            service = MonitoringService()
            result = service.test_rule(rule, request.data)
            
            return Response({
                'success': True,
                'message': 'Prueba exitosa',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error testing monitoring rule {rule.name}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error en la prueba: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Ejecutar regla de monitoreo"""
        rule = self.get_object()
        
        try:
            service = MonitoringService()
            result = service.execute_rule(rule)
            
            return Response({
                'success': True,
                'message': 'Regla ejecutada exitosamente',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error executing monitoring rule {rule.name}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error ejecutando regla: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def execute_all(self, request):
        """Ejecutar todas las reglas activas"""
        try:
            service = MonitoringService()
            result = service.execute_all_rules()
            
            return Response({
                'success': True,
                'message': 'Todas las reglas ejecutadas exitosamente',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error executing all monitoring rules: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error ejecutando reglas: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet para Alert"""
    
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AlertCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AlertUpdateSerializer
        return AlertSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        rule = self.request.query_params.get('rule')
        if rule:
            queryset = queryset.filter(rule_id=rule)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(triggered_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(triggered_at__lte=date_to)
        
        return queryset.order_by('-triggered_at')
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Reconocer alerta"""
        alert = self.get_object()
        
        if alert.status != 'active':
            return Response({
                'success': False,
                'message': 'Solo se pueden reconocer alertas activas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.save()
        
        return Response({
            'success': True,
            'message': 'Alerta reconocida exitosamente'
        })
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolver alerta"""
        alert = self.get_object()
        
        if alert.status == 'resolved':
            return Response({
                'success': False,
                'message': 'La alerta ya está resuelta'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        
        return Response({
            'success': True,
            'message': 'Alerta resuelta exitosamente'
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de alertas"""
        queryset = self.get_queryset()
        
        # Filtros de fecha
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(triggered_at__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(triggered_at__lte=date_to)
        
        stats = {
            'total_alerts': queryset.count(),
            'active_alerts': queryset.filter(status='active').count(),
            'acknowledged_alerts': queryset.filter(status='acknowledged').count(),
            'resolved_alerts': queryset.filter(status='resolved').count(),
            'by_severity': {},
            'by_status': {},
            'by_rule': {},
        }
        
        # Estadísticas por severidad
        for severity, _ in MonitoringRule.SEVERITY_LEVELS:
            count = queryset.filter(severity=severity).count()
            if count > 0:
                stats['by_severity'][severity] = count
        
        # Estadísticas por estado
        for status_choice, _ in Alert.STATUS_CHOICES:
            count = queryset.filter(status=status_choice).count()
            if count > 0:
                stats['by_status'][status_choice] = count
        
        # Estadísticas por regla
        rule_stats = queryset.values('rule__name').annotate(count=Count('id'))
        for item in rule_stats:
            stats['by_rule'][item['rule__name']] = item['count']
        
        return Response(stats)


class MetricValueViewSet(viewsets.ModelViewSet):
    """ViewSet para MetricValue"""
    
    queryset = MetricValue.objects.all()
    serializer_class = MetricValueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MetricValueCreateSerializer
        return MetricValueSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        rule = self.request.query_params.get('rule')
        if rule:
            queryset = queryset.filter(rule_id=rule)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de métricas"""
        queryset = self.get_queryset()
        
        # Filtros de fecha
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        stats = {
            'total_values': queryset.count(),
            'by_rule': {},
            'average_values': {},
            'latest_values': {},
        }
        
        # Estadísticas por regla
        rule_stats = queryset.values('rule__name').annotate(
            count=Count('id'),
            avg_value=Avg('value')
        )
        for item in rule_stats:
            stats['by_rule'][item['rule__name']] = {
                'count': item['count'],
                'average': item['avg_value']
            }
        
        # Valores promedio por regla
        for rule_name, data in stats['by_rule'].items():
            stats['average_values'][rule_name] = data['average']
        
        # Últimos valores por regla
        latest_values = queryset.values('rule__name').annotate(
            latest_value=queryset.filter(rule__name=queryset.values('rule__name')).values('value').first()
        )
        
        return Response(stats)


class HealthCheckViewSet(viewsets.ModelViewSet):
    """ViewSet para HealthCheck"""
    
    queryset = HealthCheck.objects.all()
    serializer_class = HealthCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HealthCheckCreateSerializer
        return HealthCheckSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        check_type = self.request.query_params.get('check_type')
        if check_type:
            queryset = queryset.filter(check_type=check_type)
        
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
    def execute(self, request, pk=None):
        """Ejecutar verificación de salud"""
        health_check = self.get_object()
        
        try:
            service = HealthCheckService()
            result = service.execute_health_check(health_check)
            
            return Response({
                'success': True,
                'message': 'Verificación ejecutada exitosamente',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error executing health check {health_check.name}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error ejecutando verificación: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def execute_all(self, request):
        """Ejecutar todas las verificaciones de salud"""
        try:
            service = HealthCheckService()
            result = service.execute_all_health_checks()
            
            return Response({
                'success': True,
                'message': 'Todas las verificaciones ejecutadas exitosamente',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error executing all health checks: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error ejecutando verificaciones: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de verificaciones de salud"""
        queryset = self.get_queryset()
        
        stats = {
            'total_checks': queryset.count(),
            'healthy_checks': queryset.filter(status='healthy').count(),
            'degraded_checks': queryset.filter(status='degraded').count(),
            'unhealthy_checks': queryset.filter(status='unhealthy').count(),
            'unknown_checks': queryset.filter(status='unknown').count(),
            'by_type': {},
            'by_status': {},
        }
        
        # Estadísticas por tipo
        for check_type, _ in HealthCheck.CHECK_TYPES:
            count = queryset.filter(check_type=check_type).count()
            if count > 0:
                stats['by_type'][check_type] = count
        
        # Estadísticas por estado
        for status_choice, _ in HealthCheck.STATUS_CHOICES:
            count = queryset.filter(status=status_choice).count()
            if count > 0:
                stats['by_status'][status_choice] = count
        
        return Response(stats)


class HealthCheckResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para HealthCheckResult"""
    
    queryset = HealthCheckResult.objects.all()
    serializer_class = HealthCheckResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        health_check = self.request.query_params.get('health_check')
        if health_check:
            queryset = queryset.filter(health_check_id=health_check)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(checked_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(checked_at__lte=date_to)
        
        return queryset.order_by('-checked_at')


class SystemMetricsViewSet(viewsets.ModelViewSet):
    """ViewSet para SystemMetrics"""
    
    queryset = SystemMetrics.objects.all()
    serializer_class = SystemMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SystemMetricsCreateSerializer
        return SystemMetricsSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        metric_type = self.request.query_params.get('metric_type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        metric_name = self.request.query_params.get('metric_name')
        if metric_name:
            queryset = queryset.filter(metric_name=metric_name)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de métricas del sistema"""
        queryset = self.get_queryset()
        
        # Filtros de fecha
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        stats = {
            'total_metrics': queryset.count(),
            'by_type': {},
            'by_name': {},
            'latest_values': {},
        }
        
        # Estadísticas por tipo
        for metric_type, _ in SystemMetrics.METRIC_TYPES:
            count = queryset.filter(metric_type=metric_type).count()
            if count > 0:
                stats['by_type'][metric_type] = count
        
        # Estadísticas por nombre
        name_stats = queryset.values('metric_name').annotate(count=Count('id'))
        for item in name_stats:
            stats['by_name'][item['metric_name']] = item['count']
        
        return Response(stats)


class NotificationChannelViewSet(viewsets.ModelViewSet):
    """ViewSet para NotificationChannel"""
    
    queryset = NotificationChannel.objects.all()
    serializer_class = NotificationChannelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationChannelCreateSerializer
        elif self.action == 'test':
            return NotificationChannelTestSerializer
        return NotificationChannelSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        channel_type = self.request.query_params.get('channel_type')
        if channel_type:
            queryset = queryset.filter(channel_type=channel_type)
        
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
    def test(self, request, pk=None):
        """Probar canal de notificación"""
        channel = self.get_object()
        
        try:
            service = AlertService()
            result = service.test_notification_channel(channel, request.data)
            
            return Response({
                'success': True,
                'message': 'Canal de notificación probado exitosamente',
                'data': result
            })
        except Exception as e:
            logger.error(f"Error testing notification channel {channel.name}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error probando canal: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AlertTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet para AlertTemplate"""
    
    queryset = AlertTemplate.objects.all()
    serializer_class = AlertTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AlertTemplateCreateSerializer
        return AlertTemplateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        is_default = self.request.query_params.get('is_default')
        if is_default is not None:
            queryset = queryset.filter(is_default=is_default.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-is_default', 'name')


class MonitoringDashboardViewSet(viewsets.ModelViewSet):
    """ViewSet para MonitoringDashboard"""
    
    queryset = MonitoringDashboard.objects.all()
    serializer_class = MonitoringDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MonitoringDashboardCreateSerializer
        return MonitoringDashboardSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')


class MonitoringWidgetViewSet(viewsets.ModelViewSet):
    """ViewSet para MonitoringWidget"""
    
    queryset = MonitoringWidget.objects.all()
    serializer_class = MonitoringWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MonitoringWidgetCreateSerializer
        return MonitoringWidgetSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        widget_type = self.request.query_params.get('widget_type')
        if widget_type:
            queryset = queryset.filter(widget_type=widget_type)
        
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


class MonitoringStatisticsViewSet(viewsets.ViewSet):
    """ViewSet para estadísticas generales de monitoreo"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Estadísticas generales de monitoreo"""
        try:
            # Estadísticas de reglas
            total_rules = MonitoringRule.objects.count()
            active_rules = MonitoringRule.objects.filter(is_active=True).count()
            
            # Estadísticas de alertas
            total_alerts = Alert.objects.count()
            active_alerts = Alert.objects.filter(status='active').count()
            
            # Alertas por severidad
            alerts_by_severity = {}
            for severity, _ in MonitoringRule.SEVERITY_LEVELS:
                count = Alert.objects.filter(severity=severity).count()
                if count > 0:
                    alerts_by_severity[severity] = count
            
            # Estadísticas de verificaciones de salud
            health_checks_total = HealthCheck.objects.count()
            health_checks_healthy = HealthCheck.objects.filter(status='healthy').count()
            health_checks_unhealthy = HealthCheck.objects.filter(status='unhealthy').count()
            
            # Estadísticas de métricas del sistema
            system_metrics_count = SystemMetrics.objects.count()
            
            # Estadísticas de canales de notificación
            notification_channels_count = NotificationChannel.objects.count()
            
            stats = {
                'total_rules': total_rules,
                'active_rules': active_rules,
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'alerts_by_severity': alerts_by_severity,
                'health_checks_total': health_checks_total,
                'health_checks_healthy': health_checks_healthy,
                'health_checks_unhealthy': health_checks_unhealthy,
                'system_metrics_count': system_metrics_count,
                'notification_channels_count': notification_channels_count,
            }
            
            serializer = MonitoringStatisticsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting monitoring statistics: {str(e)}")
            return Response({
                'error': 'Error obteniendo estadísticas de monitoreo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
