"""
Vistas simplificadas para el sistema de auditoría en español"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from datetime import datetime
import logging

from .models import AuditLog
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs_list(request):
    """Listar logs de auditoría - versión simplificada en español"""
    try:
        # Parámetros de filtrado
        action_filter = request.GET.get('action', '')
        user_filter = request.GET.get('user', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # Query base
        queryset = AuditLog.objects.all().order_by('-timestamp')
        
        # Aplicar filtros
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                queryset = queryset.filter(timestamp__date__gte=date_from_obj.date())
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                queryset = queryset.filter(timestamp__date__lte=date_to_obj.date())
            except ValueError:
                pass
        
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(user__username__icontains=search) |
                Q(action__icontains=search)
            )
        
        # Paginación
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        logs = queryset[start:end]
        
        # Serializar datos
        logs_data = []
        for log in logs:
            try:
                logs_data.append({
                    'id': log.id,
                    'user': log.user.username if log.user else 'Sistema',
                    'action': log.get_action_display(),
                    'action_code': log.action,
                    'action_icon': log.action_icon,
                    'action_color': log.action_color,
                    'description': log.description,
                    'ip_address': log.ip_address or 'N/A',
                    'timestamp': log.formatted_timestamp,
                    'details': log.details
                })
            except Exception as e:
                logger.warning(f"Error serializando log {log.id}: {str(e)}")
                continue
        
        return Response({
            'success': True,
            'results': logs_data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        logger.error(f"Error en audit_logs_list: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_action_choices(request):
    """Obtener opciones de acciones para filtros"""
    try:
        choices = []
        for action_code, action_display in AuditLog.ACTION_CHOICES:
            try:
                log_obj = AuditLog(action=action_code)
                choices.append({
                    'value': action_code,
                    'label': action_display,
                    'icon': log_obj.action_icon,
                    'color': log_obj.action_color
                })
            except Exception as e:
                logger.warning(f"Error procesando acción {action_code}: {str(e)}")
                continue
        
        return Response({
            'success': True,
            'choices': choices
        })
        
    except Exception as e:
        logger.error(f"Error en audit_action_choices: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )