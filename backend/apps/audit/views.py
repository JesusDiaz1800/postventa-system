from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para registros de auditoría (Solo lectura)"""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Allow admins only for unsafe methods"""
        if self.action in ['purge_logs']:
            from rest_framework.permissions import IsAdminUser
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Obtener registros de auditoría con filtros"""
        queryset = AuditLog.objects.select_related('user').all()
        
        # Filtros básicos
        action = self.request.query_params.get('action')
        user_id = self.request.query_params.get('user')
        ip_address = self.request.query_params.get('ip_address')
        search = self.request.query_params.get('search')
        
        if action:
            queryset = queryset.filter(action=action)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(description__icontains=search) | 
                Q(action__icontains=search) |
                Q(user__username__icontains=search)
            )
            
        # Filtros de fecha
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def purge_logs(self, request):
        """Action for manually purging old/invalid logs"""
        if not request.user.is_staff:
             return Response({'error': 'Unauthorized'}, status=403)
             
        # Lista exacta que el usuario quiere mantener
        allowed = [
            'user_login', 'user_logout', 
            'incident_created', 'incident_closed', 'escalation_triggered',
            'report_attached', 'create', 'delete', 'item_restored'
        ]
        
        # 1. Eliminar acciones no permitidas (antiguo purge)
        deleted_count_actions, _ = AuditLog.objects.exclude(action__in=allowed).delete()
        
        # 2. Eliminar logs basura específicos del antiguo middleware
        # Aunque la acción sea válida ('create', 'delete'), la descripción es genérica
        garbage_descriptions = [
            'Realizó acción en el sistema',
            'Creó nuevo elemento',
            'Actualizó elemento',
            'Eliminó elemento'
        ]
        
        from django.db.models import Q
        deleted_count_garbage, _ = AuditLog.objects.filter(description__in=garbage_descriptions).delete()
        
        total_deleted = deleted_count_actions + deleted_count_garbage
        
        return Response({
            'success': True, 
            'deleted': total_deleted, 
            'details': f'Acciones inválidas: {deleted_count_actions}, Basura middleware: {deleted_count_garbage}',
            'message': f'Se limpiaron {total_deleted} registros.'
        })
    
    @action(detail=False, methods=['get'])
    def action_choices(self, request):
        """Obtener opciones de acciones disponibles"""
        return Response({
            'choices': [
                {'value': k, 'label': v} 
                for k, v in AuditLog.ACTION_CHOICES
            ]
        })