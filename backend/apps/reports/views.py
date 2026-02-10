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
        
        # Average resolution time (in days) - Simplified
        try:
            resolved_with_dates = incidents_queryset.filter(
                estado='cerrado',
                fecha_cierre__isnull=False
            )
            if resolved_with_dates.exists():
                # Calculate average resolution time manually
                total_days = 0
                count = 0
                for incident in resolved_with_dates:
                    if incident.fecha_cierre and incident.created_at:
                        delta = incident.fecha_cierre - incident.created_at
                        total_days += delta.days
                        count += 1
                avg_resolution_days = total_days / count if count > 0 else 0
            else:
                avg_resolution_days = 0
        except Exception as e:
            logger.error(f"Error calculating average resolution time: {e}")
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
        
        # Incidents by month (last 12 months)
        try:
            monthly_data = []
            for i in range(12):
                month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
                month_end = month_start.replace(day=1) + timedelta(days=32)
                month_end = month_end.replace(day=1) - timedelta(days=1)
                
                month_count = incidents_queryset.filter(
                    created_at__date__range=[month_start.date(), month_end.date()]
                ).count()
                
                monthly_data.append({
                    'month': month_start.strftime('%Y-%m'),
                    'count': month_count
                })
            
            monthly_data.reverse()
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
        
        # Resolution trend (last 30 days)
        try:
            resolution_trend = []
            for i in range(30):
                date = timezone.now().date() - timedelta(days=i)
                created_count = incidents_queryset.filter(
                    created_at__date=date
                ).count()
                resolved_count = incidents_queryset.filter(
                    fecha_cierre=date
                ).count()
                
                resolution_trend.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'created': created_count,
                    'resolved': resolved_count
                })
            
            resolution_trend.reverse()
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
