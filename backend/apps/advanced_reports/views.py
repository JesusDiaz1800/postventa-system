from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json
import logging

from .models import (
    ReportTemplate, ReportInstance, ReportSchedule, 
    ReportDashboard, ReportWidget, ReportExport
)
from .serializers import (
    ReportTemplateSerializer, ReportInstanceSerializer, ReportScheduleSerializer,
    ReportDashboardSerializer, ReportWidgetSerializer, ReportExportSerializer,
    ReportGenerationSerializer, ReportScheduleCreateSerializer, ReportDashboardCreateSerializer,
    ReportWidgetCreateSerializer, ReportExportCreateSerializer, ReportStatisticsSerializer
)
from .services import ReportService, DashboardService

logger = logging.getLogger(__name__)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet para ReportTemplate"""
    
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        format_filter = self.request.query_params.get('format')
        if format_filter:
            queryset = queryset.filter(format=format_filter)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
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
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generar reporte desde plantilla"""
        template = self.get_object()
        serializer = ReportGenerationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service = ReportService()
                instance = service.generate_report(
                    template, 
                    serializer.validated_data, 
                    request.user
                )
                
                return Response({
                    'success': True,
                    'message': 'Reporte generado exitosamente',
                    'instance_id': instance.id
                })
            except Exception as e:
                logger.error(f"Error generating report from template {template.name}: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error generando reporte: {str(e)}',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Probar plantilla de reporte"""
        template = self.get_object()
        
        try:
            service = ReportService()
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
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de plantillas de reportes"""
        queryset = self.get_queryset()
        
        stats = {
            'total_templates': queryset.count(),
            'active_templates': queryset.filter(status='active').count(),
            'by_type': {},
            'by_format': {},
            'by_status': {},
        }
        
        # Estadísticas por tipo
        for report_type, _ in ReportTemplate.REPORT_TYPES:
            count = queryset.filter(report_type=report_type).count()
            if count > 0:
                stats['by_type'][report_type] = count
        
        # Estadísticas por formato
        for format_choice, _ in ReportTemplate.FORMAT_CHOICES:
            count = queryset.filter(format=format_choice).count()
            if count > 0:
                stats['by_format'][format_choice] = count
        
        # Estadísticas por estado
        for status_choice, _ in ReportTemplate.STATUS_CHOICES:
            count = queryset.filter(status=status_choice).count()
            if count > 0:
                stats['by_status'][status_choice] = count
        
        return Response(stats)


class ReportInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet para ReportInstance"""
    
    queryset = ReportInstance.objects.all()
    serializer_class = ReportInstanceSerializer
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
        
        requested_by = self.request.query_params.get('requested_by')
        if requested_by:
            queryset = queryset.filter(requested_by_id=requested_by)
        
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(requested_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(requested_at__lte=date_to)
        
        return queryset.order_by('-requested_at')
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Descargar archivo de reporte"""
        instance = self.get_object()
        
        if instance.status != 'completed' or not instance.file_path:
            return Response({
                'error': 'Reporte no disponible para descarga'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from django.http import FileResponse
            import os
            
            if os.path.exists(instance.file_path):
                return FileResponse(
                    open(instance.file_path, 'rb'),
                    as_attachment=True,
                    filename=f"{instance.template.name}.{instance.template.format}"
                )
            else:
                return Response({
                    'error': 'Archivo no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Error downloading report {instance.id}: {str(e)}")
            return Response({
                'error': 'Error descargando archivo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar generación de reporte"""
        instance = self.get_object()
        
        if instance.status not in ['pending', 'generating']:
            return Response({
                'success': False,
                'message': 'El reporte no puede ser cancelado en su estado actual'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = ReportService()
            service.cancel_report(instance, request.user)
            
            return Response({
                'success': True,
                'message': 'Reporte cancelado exitosamente'
            })
        except Exception as e:
            logger.error(f"Error cancelling report {instance.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error cancelando reporte: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Exportar reporte en formato diferente"""
        instance = self.get_object()
        serializer = ReportExportCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service = ReportService()
                export = service.export_report(instance, serializer.validated_data, request.user)
                
                return Response({
                    'success': True,
                    'message': 'Exportación iniciada',
                    'export_id': export.id
                })
            except Exception as e:
                logger.error(f"Error exporting report {instance.id}: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error exportando reporte: {str(e)}',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de instancias de reportes"""
        queryset = self.get_queryset()
        
        # Filtros de fecha
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(requested_at__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(requested_at__lte=date_to)
        
        stats = {
            'total_instances': queryset.count(),
            'by_status': {},
            'by_template': {},
            'success_rate': 0,
            'average_generation_time': 0,
        }
        
        # Estadísticas por estado
        for status_choice, _ in ReportInstance.STATUS_CHOICES:
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


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet para ReportSchedule"""
    
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
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
        
        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('name')
    
    @action(detail=True, methods=['post'])
    def execute_now(self, request, pk=None):
        """Ejecutar programación inmediatamente"""
        schedule = self.get_object()
        
        try:
            service = ReportService()
            instance = service.execute_schedule(schedule, request.user)
            
            return Response({
                'success': True,
                'message': 'Programación ejecutada exitosamente',
                'instance_id': instance.id
            })
        except Exception as e:
            logger.error(f"Error executing schedule {schedule.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error ejecutando programación: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pausar programación"""
        schedule = self.get_object()
        
        if schedule.status != 'active':
            return Response({
                'success': False,
                'message': 'Solo se pueden pausar programaciones activas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        schedule.status = 'paused'
        schedule.save()
        
        return Response({
            'success': True,
            'message': 'Programación pausada exitosamente'
        })
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Reanudar programación"""
        schedule = self.get_object()
        
        if schedule.status != 'paused':
            return Response({
                'success': False,
                'message': 'Solo se pueden reanudar programaciones pausadas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        schedule.status = 'active'
        schedule.save()
        
        return Response({
            'success': True,
            'message': 'Programación reanudada exitosamente'
        })


class ReportDashboardViewSet(viewsets.ModelViewSet):
    """ViewSet para ReportDashboard"""
    
    queryset = ReportDashboard.objects.all()
    serializer_class = ReportDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Obtener datos del dashboard"""
        dashboard = self.get_object()
        
        try:
            service = DashboardService()
            data = service.get_dashboard_data(dashboard, request.query_params)
            
            return Response({
                'success': True,
                'data': data
            })
        except Exception as e:
            logger.error(f"Error getting dashboard data {dashboard.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo datos: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Refrescar datos del dashboard"""
        dashboard = self.get_object()
        
        try:
            service = DashboardService()
            service.refresh_dashboard(dashboard)
            
            return Response({
                'success': True,
                'message': 'Dashboard refrescado exitosamente'
            })
        except Exception as e:
            logger.error(f"Error refreshing dashboard {dashboard.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error refrescando dashboard: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ReportWidgetViewSet(viewsets.ModelViewSet):
    """ViewSet para ReportWidget"""
    
    queryset = ReportWidget.objects.all()
    serializer_class = ReportWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        dashboard = self.request.query_params.get('dashboard')
        if dashboard:
            queryset = queryset.filter(dashboard_id=dashboard)
        
        widget_type = self.request.query_params.get('widget_type')
        if widget_type:
            queryset = queryset.filter(widget_type=widget_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('order', 'name')
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Obtener datos del widget"""
        widget = self.get_object()
        
        try:
            service = DashboardService()
            data = service.get_widget_data(widget, request.query_params)
            
            return Response({
                'success': True,
                'data': data
            })
        except Exception as e:
            logger.error(f"Error getting widget data {widget.id}: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error obteniendo datos: {str(e)}',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ReportExportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para ReportExport"""
    
    queryset = ReportExport.objects.all()
    serializer_class = ReportExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        instance = self.request.query_params.get('instance')
        if instance:
            queryset = queryset.filter(instance_id=instance)
        
        export_format = self.request.query_params.get('export_format')
        if export_format:
            queryset = queryset.filter(export_format=export_format)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-requested_at')
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Descargar archivo exportado"""
        export = self.get_object()
        
        if export.status != 'completed' or not export.file_path:
            return Response({
                'error': 'Exportación no disponible para descarga'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from django.http import FileResponse
            import os
            
            if os.path.exists(export.file_path):
                return FileResponse(
                    open(export.file_path, 'rb'),
                    as_attachment=True,
                    filename=f"{export.instance.template.name}.{export.export_format}"
                )
            else:
                return Response({
                    'error': 'Archivo no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Error downloading export {export.id}: {str(e)}")
            return Response({
                'error': 'Error descargando archivo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
