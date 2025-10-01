"""
Vistas para el sistema de auditoría
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from apps.users.permissions import RoleBasedPermission
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import AuditLog
from .serializers import AuditLogSerializer, AuditLogListSerializer, AuditLogFilterSerializer

logger = logging.getLogger(__name__)


class AuditPermission(BasePermission):
    """
    Permiso para acceder a logs de auditoría
    Solo administradores y supervisores pueden ver los logs
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Permitir acceso a administradores y supervisores
        return request.user.role in ['admin', 'supervisor']


class AuditLogFilter(filters.FilterSet):
    """Filtros para logs de auditoría"""
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    action = filters.ChoiceFilter(choices=AuditLog.ACTION_CHOICES)
    resource_type = filters.ChoiceFilter(choices=AuditLog.RESOURCE_TYPE_CHOICES)
    start_date = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='created_at', lookup_expr='lte')
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = AuditLog
        fields = ['user', 'action', 'resource_type', 'start_date', 'end_date', 'search']
    
    def filter_search(self, queryset, name, value):
        """Filtro de búsqueda general"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(action__icontains=value) |
            Q(resource_type__icontains=value) |
            Q(details__icontains=value) |
            Q(resource_id__icontains=value)
        )


class AuditLogListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear logs de auditoría"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogListSerializer
    permission_classes = [IsAuthenticated, AuditPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuditLogFilter
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Obtener queryset con filtros aplicados"""
        queryset = super().get_queryset()
        
        # Aplicar filtros adicionales si es necesario
        return queryset.select_related('user')


class AuditLogRetrieveView(generics.RetrieveAPIView):
    """Vista para obtener un log de auditoría específico"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


@api_view(['GET'])
@permission_classes([IsAuthenticated, AuditPermission])
def audit_logs_list(request):
    """Listar logs de auditoría con filtros"""
    try:
        # Obtener parámetros de filtro
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        
        filters_data = {
            'user': request.GET.get('user', ''),
            'action': request.GET.get('action', ''),
            'resource_type': request.GET.get('resource_type', ''),
            'start_date': start_date if start_date else None,
            'end_date': end_date if end_date else None,
            'search': request.GET.get('search', ''),
        }
        
        # Validar filtros
        filter_serializer = AuditLogFilterSerializer(data=filters_data)
        if not filter_serializer.is_valid():
            return Response(
                {'error': 'Filtros inválidos', 'details': filter_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Construir queryset
        queryset = AuditLog.objects.select_related('user').order_by('-created_at')
        
        # Aplicar filtros
        if filters_data['user']:
            queryset = queryset.filter(user__username__icontains=filters_data['user'])
        
        if filters_data['action']:
            queryset = queryset.filter(action=filters_data['action'])
        
        if filters_data['resource_type']:
            queryset = queryset.filter(resource_type=filters_data['resource_type'])
        
        if filters_data['start_date']:
            start_date = datetime.strptime(filters_data['start_date'], '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        if filters_data['end_date']:
            end_date = datetime.strptime(filters_data['end_date'], '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        if filters_data['search']:
            search_term = filters_data['search']
            queryset = queryset.filter(
                Q(user__username__icontains=search_term) |
                Q(action__icontains=search_term) |
                Q(resource_type__icontains=search_term) |
                Q(details__icontains=search_term) |
                Q(resource_id__icontains=search_term)
            )
        
        # Paginación
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        total_count = queryset.count()
        logs = queryset[start_index:end_index]
        
        # Serializar datos
        serializer = AuditLogListSerializer(logs, many=True)
        
        return Response({
            'success': True,
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        logger.error(f"Error listando logs de auditoría: {e}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, AuditPermission])
def audit_logs_export(request):
    """Exportar logs de auditoría"""
    try:
        # Obtener parámetros de filtro (mismo que en list)
        filters_data = {
            'user': request.GET.get('user', ''),
            'action': request.GET.get('action', ''),
            'resource_type': request.GET.get('resource_type', ''),
            'start_date': request.GET.get('start_date', ''),
            'end_date': request.GET.get('end_date', ''),
            'search': request.GET.get('search', ''),
        }
        
        # Construir queryset (mismo filtrado que en list)
        queryset = AuditLog.objects.select_related('user').order_by('-created_at')
        
        # Aplicar filtros
        if filters_data['user']:
            queryset = queryset.filter(user__username__icontains=filters_data['user'])
        
        if filters_data['action']:
            queryset = queryset.filter(action=filters_data['action'])
        
        if filters_data['resource_type']:
            queryset = queryset.filter(resource_type=filters_data['resource_type'])
        
        if filters_data['start_date']:
            start_date = datetime.strptime(filters_data['start_date'], '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        if filters_data['end_date']:
            end_date = datetime.strptime(filters_data['end_date'], '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        if filters_data['search']:
            search_term = filters_data['search']
            queryset = queryset.filter(
                Q(user__username__icontains=search_term) |
                Q(action__icontains=search_term) |
                Q(resource_type__icontains=search_term) |
                Q(details__icontains=search_term) |
                Q(resource_id__icontains=search_term)
            )
        
        # Limitar a los últimos 1000 registros para exportación
        logs = queryset[:1000]
        
        # Serializar datos
        serializer = AuditLogListSerializer(logs, many=True)
        
        # Log de la exportación
        from .models import AuditLogManager
        AuditLogManager.log_user_action(
            user=request.user,
            action='export',
            details=f'Exportó {len(logs)} logs de auditoría',
            request=request
        )
        
        return Response({
            'success': True,
            'data': serializer.data,
            'exported_at': timezone.now().isoformat(),
            'total_exported': len(logs)
        })
        
    except Exception as e:
        logger.error(f"Error exportando logs de auditoría: {e}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def audit_logs_statistics(request):
    """Obtener estadísticas de logs de auditoría"""
    try:
        # Estadísticas generales
        total_logs = AuditLog.objects.count()
        
        # Logs por acción
        action_stats = {}
        for action, _ in AuditLog.ACTION_CHOICES:
            count = AuditLog.objects.filter(action=action).count()
            if count > 0:
                action_stats[action] = count
        
        # Logs por tipo de recurso
        resource_stats = {}
        for resource_type, _ in AuditLog.RESOURCE_TYPE_CHOICES:
            count = AuditLog.objects.filter(resource_type=resource_type).count()
            if count > 0:
                resource_stats[resource_type] = count
        
        # Logs por usuario (top 10)
        user_stats = AuditLog.objects.values('user__username').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Logs por día (últimos 30 días) - simplificado
        thirty_days_ago = timezone.now() - timedelta(days=30)
        try:
            daily_stats = AuditLog.objects.filter(
                created_at__gte=thirty_days_ago
            ).values('created_at__date').annotate(
                count=Count('id')
            ).order_by('created_at__date')
        except Exception as e:
            logger.warning(f"Error en consulta diaria: {e}")
            daily_stats = []
        
        return Response({
            'success': True,
            'statistics': {
                'total_logs': total_logs,
                'action_stats': action_stats,
                'resource_stats': resource_stats,
                'user_stats': list(user_stats),
                'daily_stats': list(daily_stats)
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de auditoría: {e}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )