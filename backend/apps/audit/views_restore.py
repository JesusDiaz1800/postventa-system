
from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.utils import timezone
from .models import DeletedItem
from .serializers import DeletedItemSerializer, DeletedItemRestoreSerializer, UserSerializer

class CanRestoreDeletedItems(permissions.BasePermission):
    """Solo admins pueden ver y restaurar items eliminados"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class DeletedItemViewSet(viewsets.ModelViewSet):
    """
    Vista para listar, restaurar y eliminar permanentemente elementos.
    """
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    serializer_class = DeletedItemSerializer
    permission_classes = [CanRestoreDeletedItems]
    
    def get_queryset(self):
        # Filtrar solo items que aún no han expirado
        return DeletedItem.objects.filter(
            restore_deadline__gt=timezone.now()
        ).select_related('deleted_by').order_by('-deleted_at')
        
    @decorators.action(detail=True, methods=['post'], serializer_class=DeletedItemRestoreSerializer)
    def restore(self, request, pk=None):
        deleted_item = self.get_object()
        
        # Verificar deadline una vez más
        if deleted_item.restore_deadline < timezone.now():
            return Response(
                {"error": "Este elemento ha expirado y no se puede restaurar."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = DeletedItemRestoreSerializer(data=request.data)
        if serializer.is_valid():
            try:
                restored_object = serializer.restore(deleted_item)
                return Response({
                    "success": True, 
                    "message": f"Elemento restaurado exitosamente: {restored_object}",
                    "id": restored_object.pk
                })
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
