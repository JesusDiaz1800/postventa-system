import django_filters
from django.db.models import Q
from .models import AuditLog


class AuditLogFilter(django_filters.FilterSet):
    """Filter for audit logs"""
    
    # Date filters
    created_at_from = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Fecha desde'
    )
    
    created_at_to = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Fecha hasta'
    )
    
    # Action and resource filters
    action = django_filters.ChoiceFilter(
        choices=AuditLog.ACTION_CHOICES,
        help_text='Acción realizada'
    )
    
    resource_type = django_filters.ChoiceFilter(
        choices=AuditLog.RESOURCE_TYPE_CHOICES,
        help_text='Tipo de recurso'
    )
    
    resource_id = django_filters.CharFilter(
        field_name='resource_id',
        help_text='ID del recurso'
    )
    
    # User filter
    user = django_filters.NumberFilter(
        field_name='user',
        help_text='ID del usuario'
    )
    
    # IP filter
    ip_address = django_filters.CharFilter(
        field_name='ip_address',
        help_text='Dirección IP'
    )
    
    # Complex search
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Búsqueda general en descripción, nombre de recurso, usuario'
    )
    
    class Meta:
        model = AuditLog
        fields = [
            'action', 'resource_type', 'resource_id', 'user', 'ip_address',
            'created_at_from', 'created_at_to', 'search'
        ]
    
    def filter_search(self, queryset, name, value):
        """General search across multiple fields"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(description__icontains=value) |
            Q(resource_name__icontains=value) |
            Q(user__username__icontains=value) |
            Q(details_json__icontains=value)
        )
