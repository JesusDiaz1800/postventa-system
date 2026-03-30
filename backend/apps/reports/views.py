"""
Views for reports and analytics
"""

import logging
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.users.permissions import RoleBasedPermission
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from apps.incidents.models import Incident
from apps.documents.models import VisitReport, SupplierReport, LabReport, QualityReport
from apps.users.models import User
from django.db.models.functions import TruncMonth, TruncDay

logger = logging.getLogger(__name__)


class ReportsDashboardView:
    """Vista para el dashboard de reportes con permisos basados en roles"""
    required_roles = ['admin', 'supervisor', 'analyst', 'management']

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reports_dashboard(request):
    """Get comprehensive reports data"""
    if not request.user.can_view_reports():
        return Response({'error': 'No tiene permisos para ver reportes'}, status=status.HTTP_403_FORBIDDEN)
    
    logger.info(f"=== REPORTS DASHBOARD REQUEST ===")
    logger.info(f"User: {request.user}")
    logger.info(f"User authenticated: {request.user.is_authenticated}")
    logger.info(f"Auth header: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
    
    try:
        # Get date filters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        provider = request.GET.get('provider', '')
        status_filter = request.GET.get('status', '')
        
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (timezone.now() - timedelta(days=30)).date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
        if not end_date:
            end_date = timezone.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Base queryset (without default ordering to avoid SQL Server GROUP BY issues)
        incidents_queryset = Incident.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).order_by()
        
        # Apply filters
        if provider:
            incidents_queryset = incidents_queryset.filter(provider__icontains=provider)
        if status_filter:
            incidents_queryset = incidents_queryset.filter(estado=status_filter)
        
        # Calculate metrics
        total_incidents = incidents_queryset.count()
        resolved_incidents = incidents_queryset.filter(estado='cerrado').count()
        pending_incidents = incidents_queryset.filter(estado__in=['abierto', 'en_progreso']).count()
        
        # Average resolution time (en días) - OPTIMIZADO: Agregación en BD
        try:
            from django.db.models import F, ExpressionWrapper, DurationField
            # Nota: SQL Server maneja las deltas de fecha de forma particular,
            # pero Django MSSQL Backend traduce esto correctamente entre datetime2 y duration.
            avg_metrics = incidents_queryset.filter(
                estado='cerrado',
                fecha_cierre__isnull=False
            ).annotate(
                latency=ExpressionWrapper(
                    F('fecha_cierre') - F('created_at__date'), 
                    output_field=DurationField()
                )
            ).aggregate(avg_latency=Avg('latency'))
            
            delta = avg_metrics.get('avg_latency')
            avg_resolution_days = delta.days if delta else 0
        except Exception as e:
            logger.error(f"Error calculando tiempo promedio de resolución (SQL): {e}")
            avg_resolution_days = 0
        
        # Incidents by status
        try:
            incidents_by_status = list(incidents_queryset.values('estado').annotate(
                count=Count('id')
            ).order_by('-count'))
        except Exception as e:
            logger.error(f"Error getting incidents by status: {e}")
            incidents_by_status = []
        
        # Incidents by priority
        try:
            incidents_by_priority = list(incidents_queryset.values('prioridad').annotate(
                count=Count('id')
            ).order_by('-count'))
        except Exception as e:
            logger.error(f"Error getting incidents by priority: {e}")
            incidents_by_priority = []
        
        # Incidents by provider
        try:
            incidents_by_provider = list(incidents_queryset.values(
                'provider'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10])
        except Exception as e:
            logger.error(f"Error getting incidents by provider: {e}")
            incidents_by_provider = []
        
        # Incidents by month (last 12 months) - OPTIMIZADO
        try:
            twelve_months_ago = timezone.now().replace(day=1) - timedelta(days=365)
            monthly_data_raw = incidents_queryset.filter(
                created_at__gte=twelve_months_ago
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')

            monthly_data = [
                {
                    'month': item['month'].strftime('%Y-%m') if item['month'] else 'N/A',
                    'count': item['count']
                } for item in monthly_data_raw
            ]
        except Exception as e:
            logger.error(f"Error getting monthly data: {e}")
            monthly_data = []
        
        # Top SKUs
        try:
            top_skus = list(incidents_queryset.values('sku').annotate(
                count=Count('id')
            ).order_by('-count')[:10])
        except Exception as e:
            logger.error(f"Error getting top SKUs: {e}")
            top_skus = []
        
        # Resolution trend (last 30 days) - OPTIMIZADO
        try:
            thirty_days_ago = timezone.now().date() - timedelta(days=30)
            
            # Creados por día
            created_trend = incidents_queryset.filter(
                created_at__date__gte=thirty_days_ago
            ).annotate(
                day=TruncDay('created_at')
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            # Cerrados por día
            resolved_trend_raw = incidents_queryset.filter(
                estado='cerrado',
                fecha_cierre__gte=thirty_days_ago
            ).values('fecha_cierre').annotate(
                count=Count('id')
            ).order_by('fecha_cierre')
            
            # Mapear datos para el frontend
            trend_map = {}
            for item in created_trend:
                d = item['day'].strftime('%Y-%m-%d')
                trend_map[d] = {'date': d, 'created': item['count'], 'resolved': 0}
            
            for item in resolved_trend_raw:
                d = item['fecha_cierre'].strftime('%Y-%m-%d') if hasattr(item['fecha_cierre'], 'strftime') else str(item['fecha_cierre'])
                if d in trend_map:
                    trend_map[d]['resolved'] = item['count']
                else:
                    trend_map[d] = {'date': d, 'created': 0, 'resolved': item['count']}
            
            resolution_trend = sorted(trend_map.values(), key=lambda x: x['date'])
        except Exception as e:
            logger.error(f"Error getting resolution trend: {e}")
            resolution_trend = []
        
        # Documents generated
        try:
            visit_count = VisitReport.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count()
            supplier_count = SupplierReport.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count()
            lab_count = LabReport.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count()
            quality_count = QualityReport.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count()
            
            documents_count = visit_count + supplier_count + lab_count + quality_count
        except Exception as e:
            logger.error(f"Error getting documents count: {e}")
            documents_count = 0
        
        # Active users
        try:
            active_users = User.objects.filter(
                last_login__date__range=[start_date, end_date]
            ).count()
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            active_users = 0
        
        return Response({
            'total_incidents': total_incidents,
            'resolved_incidents': resolved_incidents,
            'pending_incidents': pending_incidents,
            'average_resolution_time': avg_resolution_days,
            'incidents_by_status': incidents_by_status,
            'incidents_by_priority': incidents_by_priority,
            'incidents_by_provider': incidents_by_provider,
            'incidents_by_month': monthly_data,
            'top_skus': top_skus,
            'resolution_trend': resolution_trend,
            'documents_generated': documents_count,
            'active_users': active_users,
            'filters': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'provider': provider,
                'status': status_filter
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating reports: {str(e)}", exc_info=True)
        return Response({
            'error': 'Error al generar el dashboard de reportes. Por favor contacte al administrador.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_reports(request):
    """Export reports data in various formats"""
    try:
        format_type = request.GET.get('format', 'json')
        
        # Get the same data as dashboard
        dashboard_response = reports_dashboard(request)
        
        if dashboard_response.status_code != 200:
            return dashboard_response
        
        data = dashboard_response.data
        
        if format_type == 'json':
            return Response(data, status=status.HTTP_200_OK)
        elif format_type == 'csv':
            # For CSV export, we would generate CSV format
            # This is a simplified version
            return Response({
                'message': 'CSV export not implemented yet',
                'data': data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Unsupported format'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': f'Error exporting reports: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
