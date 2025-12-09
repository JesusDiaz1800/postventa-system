"""
<<<<<<< HEAD
Vistas simples para el sistema de auditoría
=======
Vistas simplificadas para el sistema de auditoría en español
>>>>>>> 674c244 (tus cambios)
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
<<<<<<< HEAD
import logging

=======
from django.db.models import Q
from datetime import datetime
import logging

from .models import AuditLog

>>>>>>> 674c244 (tus cambios)
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
<<<<<<< HEAD
def audit_logs_list_simple(request):
    """Lista simple de logs de auditoría"""
    try:
        # Por ahora, devolver datos de prueba
        sample_logs = [
            {
                'id': 1,
                'user': 'admin',
                'action': 'login',
                'resource_type': 'system',
                'resource_id': '1',
                'details': 'Usuario inició sesión en el sistema',
                'ip_address': '127.0.0.1',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'created_at': '2025-09-29T13:30:00Z'
            },
            {
                'id': 2,
                'user': 'admin',
                'action': 'create',
                'resource_type': 'incident',
                'resource_id': '1',
                'details': 'Creó nueva incidencia INC-2025-0001',
                'ip_address': '127.0.0.1',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'created_at': '2025-09-29T13:31:00Z'
            },
            {
                'id': 3,
                'user': 'admin',
                'action': 'upload',
                'resource_type': 'document',
                'resource_id': '1',
                'details': 'Subió documento de reporte de visita',
                'ip_address': '127.0.0.1',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'created_at': '2025-09-29T13:32:00Z'
            }
        ]
        
        return Response({
            'success': True,
            'results': sample_logs,
            'count': len(sample_logs),
            'page': 1,
            'page_size': 50,
            'total_pages': 1
        })
        
    except Exception as e:
        logger.error(f"Error en audit_logs_list_simple: {e}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
=======
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
>>>>>>> 674c244 (tus cambios)
