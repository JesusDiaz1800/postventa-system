"""
Vistas corregidas para el sistema de auditoría
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import logging

from .models import AuditLog

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs_list_fixed(request):
    """Listar logs de auditoría con filtros - versión corregida"""
    try:
        # Obtener parámetros de filtro
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        user_filter = request.GET.get('user', '')
        action_filter = request.GET.get('action', '')
        resource_type_filter = request.GET.get('resource_type', '')
        search_term = request.GET.get('search', '')
        
        # Construir queryset básico
        queryset = AuditLog.objects.select_related('user').order_by('-created_at')
        
        # Aplicar filtros de manera segura
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)
        
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        
        if resource_type_filter:
            queryset = queryset.filter(resource_type=resource_type_filter)
        
        # Filtros de fecha con validación
        if start_date:
            try:
                from datetime import datetime
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_date_obj)
            except ValueError:
                pass  # Ignorar fechas inválidas
        
        if end_date:
            try:
                from datetime import datetime
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_date_obj)
            except ValueError:
                pass  # Ignorar fechas inválidas
        
        # Búsqueda general
        if search_term:
            queryset = queryset.filter(
                Q(user__username__icontains=search_term) |
                Q(action__icontains=search_term) |
                Q(resource_type__icontains=search_term) |
                Q(details__icontains=search_term) |
                Q(resource_id__icontains=search_term)
            )
        
        # Paginación
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 50)), 100)  # Máximo 100 por página
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        total_count = queryset.count()
        logs = queryset[start_index:end_index]
        
        # Serializar datos de manera simple
        results = []
        for log in logs:
            results.append({
                'id': log.id,
                'user': log.user.username if log.user else 'Sistema',
                'action': log.action,
                'action_display': log.action_display,
                'resource_type': log.resource_type,
                'resource_type_display': log.resource_type_display,
                'resource_id': log.resource_id,
                'details': log.details,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'created_at': log.created_at.isoformat(),
                'created_at_display': log.created_at_display,
                'metadata': log.metadata
            })
        
        return Response({
            'success': True,
            'results': results,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        logger.error(f"Error listando logs de auditoría: {e}")
        return Response(
            {'error': 'Error interno del servidor', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs_simple(request):
    """Lista simple de logs de auditoría sin filtros complejos"""
    try:
        # Obtener logs recientes
        logs = AuditLog.objects.select_related('user').order_by('-created_at')[:50]
        
        results = []
        for log in logs:
            results.append({
                'id': log.id,
                'user': log.user.username if log.user else 'Sistema',
                'action': log.action,
                'action_display': log.action_display,
                'resource_type': log.resource_type,
                'resource_type_display': log.resource_type_display,
                'resource_id': log.resource_id,
                'details': log.details,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat(),
                'created_at_display': log.created_at_display
            })
        
        return Response({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error listando logs simples: {e}")
        return Response(
            {'error': 'Error interno del servidor', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
