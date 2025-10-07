from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
import csv
import json
from io import StringIO

from .models import AuditLog, AuditRule, AuditReport, AuditDashboard, AuditAlert
from .serializers import (
    AuditLogSerializer,
    AuditLogCreateSerializer,
    AuditRuleSerializer,
    AuditReportSerializer,
    AuditReportCreateSerializer,
    AuditDashboardSerializer,
    AuditAlertSerializer,
    AuditAlertActionSerializer,
    AuditStatsSerializer,
    AuditSearchSerializer,
    AuditExportSerializer,
    AuditRealTimeSerializer
)
from .services import AuditService


class AuditLogViewSet(viewsets.ModelViewSet):
    """ViewSet para registros de auditoría"""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener registros de auditoría con filtros"""
        queryset = AuditLog.objects.all()
        
        # Filtros básicos
        action = self.request.query_params.get('action')
        result = self.request.query_params.get('result')
        user_id = self.request.query_params.get('user')
        severity = self.request.query_params.get('severity')
        category = self.request.query_params.get('category')
        ip_address = self.request.query_params.get('ip_address')
        module = self.request.query_params.get('module')
        
        if action:
            queryset = queryset.filter(action=action)
        if result:
            queryset = queryset.filter(result=result)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if severity:
            queryset = queryset.filter(severity=severity)
        if category:
            queryset = queryset.filter(category=category)
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        if module:
            queryset = queryset.filter(module=module)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar serializer de creación para POST"""
        if self.action == 'create':
            return AuditLogCreateSerializer
        return AuditLogSerializer
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Obtener registros recientes"""
        limit = int(request.query_params.get('limit', 50))
        logs = self.get_queryset()[:limit]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_severity(self, request):
        """Obtener registros de alta severidad"""
        logs = self.get_queryset().filter(severity__in=['high', 'critical'])
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed_actions(self, request):
        """Obtener acciones fallidas"""
        logs = self.get_queryset().filter(result='failure')
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Obtener registros por usuario"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id requerido'}, status=400)
        
        logs = self.get_queryset().filter(user_id=user_id)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_ip(self, request):
        """Obtener registros por IP"""
        ip_address = request.query_params.get('ip_address')
        if not ip_address:
            return Response({'error': 'ip_address requerido'}, status=400)
        
        logs = self.get_queryset().filter(ip_address=ip_address)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Buscar registros de auditoría"""
        serializer = AuditSearchSerializer(data=request.data)
        if serializer.is_valid():
            results = AuditService.search_audit_logs(serializer.validated_data)
            return Response(results)
        return Response(serializer.errors, status=400)
    
    @action(detail=False, methods=['post'])
    def export(self, request):
        """Exportar registros de auditoría"""
        serializer = AuditExportSerializer(data=request.data)
        if serializer.is_valid():
            export_data = AuditService.export_audit_logs(serializer.validated_data)
            
            format_type = serializer.validated_data['format']
            
            if format_type == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
                
                writer = csv.writer(response)
                writer.writerow(['Timestamp', 'Action', 'User', 'Result', 'Severity', 'Category', 'Description', 'IP Address', 'Module'])
                
                for log in export_data:
                    writer.writerow([
                        log.formatted_timestamp,
                        log.get_action_display(),
                        log.user.username if log.user else 'Sistema',
                        log.get_result_display(),
                        log.get_severity_display(),
                        log.get_category_display(),
                        log.description,
                        log.ip_address,
                        log.module
                    ])
                
                return response
            
            elif format_type == 'json':
                response = HttpResponse(content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="audit_logs.json"'
                
                data = AuditLogSerializer(export_data, many=True).data
                response.write(json.dumps(data, indent=2))
                return response
            
            else:
                return Response({'error': 'Formato no soportado'}, status=400)
        
        return Response(serializer.errors, status=400)


class AuditRuleViewSet(viewsets.ModelViewSet):
    """ViewSet para reglas de auditoría"""
    serializer_class = AuditRuleSerializer
    permission_classes = [IsAuthenticated]
    queryset = AuditRule.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Probar regla de auditoría"""
        rule = self.get_object()
        test_data = request.data
        
        result = AuditService.test_audit_rule(rule, test_data)
        return Response(result)


class AuditReportViewSet(viewsets.ModelViewSet):
    """ViewSet para reportes de auditoría"""
    serializer_class = AuditReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener reportes del usuario"""
        return AuditReport.objects.filter(created_by=self.request.user)
    
    def get_serializer_class(self):
        """Usar serializer de creación para POST"""
        if self.action == 'create':
            return AuditReportCreateSerializer
        return AuditReportSerializer
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generar reporte"""
        report = self.get_object()
        if report.status != 'pending':
            return Response({'error': 'Reporte ya generado'}, status=400)
        
        AuditService.generate_audit_report(report)
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Descargar reporte"""
        report = self.get_object()
        if not report.is_completed or not report.file_path:
            return Response({'error': 'Reporte no disponible'}, status=404)
        
        try:
            with open(report.file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{report.name}.pdf"'
                return response
        except FileNotFoundError:
            return Response({'error': 'Archivo no encontrado'}, status=404)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Obtener plantillas de reporte"""
        templates = AuditService.get_report_templates()
        return Response(templates)


class AuditDashboardViewSet(viewsets.ModelViewSet):
    """ViewSet para dashboards de auditoría"""
    serializer_class = AuditDashboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener dashboards del usuario"""
        return AuditDashboard.objects.filter(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Obtener datos del dashboard"""
        dashboard = self.get_object()
        data = AuditService.get_dashboard_data(dashboard, request.query_params)
        return Response(data)


class AuditAlertViewSet(viewsets.ModelViewSet):
    """ViewSet para alertas de auditoría"""
    serializer_class = AuditAlertSerializer
    permission_classes = [IsAuthenticated]
    queryset = AuditAlert.objects.all()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Obtener alertas activas"""
        alerts = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_severity(self, request):
        """Obtener alertas de alta severidad"""
        alerts = self.get_queryset().filter(severity__in=['high', 'critical'])
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolver alerta"""
        alert = self.get_object()
        notes = request.data.get('notes', '')
        alert.resolve(request.user, notes)
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Reconocer alerta"""
        alert = self.get_object()
        alert.acknowledge(request.user)
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Descartar alerta"""
        alert = self.get_object()
        alert.dismiss(request.user)
        serializer = self.get_serializer(alert)
        return Response(serializer.data)


class AuditStatsViewSet(viewsets.ViewSet):
    """ViewSet para estadísticas de auditoría"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Obtener estadísticas generales"""
        stats = AuditService.get_audit_stats()
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def real_time(self, request):
        """Obtener datos en tiempo real"""
        data = AuditService.get_real_time_data()
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Obtener tendencias"""
        period = request.query_params.get('period', '24h')
        trends = AuditService.get_audit_trends(period)
        return Response(trends)
    
    @action(detail=False, methods=['get'])
    def top_users(self, request):
        """Obtener top usuarios"""
        limit = int(request.query_params.get('limit', 10))
        top_users = AuditService.get_top_users(limit)
        return Response(top_users)
    
    @action(detail=False, methods=['get'])
    def top_actions(self, request):
        """Obtener top acciones"""
        limit = int(request.query_params.get('limit', 10))
        top_actions = AuditService.get_top_actions(limit)
        return Response(top_actions)
    
    @action(detail=False, methods=['get'])
    def security_events(self, request):
        """Obtener eventos de seguridad"""
        events = AuditService.get_security_events()
        return Response(events)
    
    @action(detail=False, methods=['get'])
    def performance_metrics(self, request):
        """Obtener métricas de rendimiento"""
        metrics = AuditService.get_performance_metrics()
        return Response(metrics)


class AuditSearchViewSet(viewsets.ViewSet):
    """ViewSet para búsqueda avanzada de auditoría"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def advanced(self, request):
        """Búsqueda avanzada"""
        search_params = request.data
        results = AuditService.advanced_search(search_params)
        return Response(results)
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Obtener sugerencias de búsqueda"""
        query = request.query_params.get('q', '')
        suggestions = AuditService.get_search_suggestions(query)
        return Response(suggestions)
    
    @action(detail=False, methods=['get'])
    def filters(self, request):
        """Obtener filtros disponibles"""
        filters = AuditService.get_available_filters()
        return Response(filters)