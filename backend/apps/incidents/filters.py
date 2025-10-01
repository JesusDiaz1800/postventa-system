import django_filters
from django.db.models import Q
from .models import Incident


class IncidentFilter(django_filters.FilterSet):
    """Filter for incidents"""
    
    # Date filters
    fecha_deteccion_from = django_filters.DateFilter(
        field_name='fecha_deteccion',
        lookup_expr='gte',
        help_text='Fecha de detección desde'
    )
    
    fecha_deteccion_to = django_filters.DateFilter(
        field_name='fecha_deteccion',
        lookup_expr='lte',
        help_text='Fecha de detección hasta'
    )
    
    created_at_from = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Fecha de creación desde'
    )
    
    created_at_to = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Fecha de creación hasta'
    )
    
    # Status and priority filters
    estado = django_filters.ChoiceFilter(
        choices=Incident.STATUS_CHOICES,
        help_text='Estado de la incidencia'
    )
    
    prioridad = django_filters.ChoiceFilter(
        choices=Incident.PRIORITY_CHOICES,
        help_text='Prioridad de la incidencia'
    )
    
    categoria = django_filters.ChoiceFilter(
        choices=Incident.CATEGORY_CHOICES,
        help_text='Categoría del producto'
    )
    
    # Assignment filters
    assigned_to = django_filters.NumberFilter(
        field_name='assigned_to',
        help_text='ID del usuario asignado'
    )
    
    created_by = django_filters.NumberFilter(
        field_name='created_by',
        help_text='ID del usuario que creó la incidencia'
    )
    
    # lab_required field removed
    
    # Text search filters
    cliente = django_filters.CharFilter(
        field_name='cliente',
        lookup_expr='icontains',
        help_text='Nombre del cliente'
    )
    
    provider = django_filters.CharFilter(
        field_name='provider',
        lookup_expr='icontains',
        help_text='Proveedor'
    )
    
    obra = django_filters.CharFilter(
        field_name='obra',
        lookup_expr='icontains',
        help_text='Obra o proyecto'
    )
    
    sku = django_filters.CharFilter(
        field_name='sku',
        lookup_expr='icontains',
        help_text='SKU del producto'
    )
    
    lote = django_filters.CharFilter(
        field_name='lote',
        lookup_expr='icontains',
        help_text='Número de lote'
    )
    
    # Complex search
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Búsqueda general en código, cliente, proveedor, obra, SKU, lote'
    )
    
    class Meta:
        model = Incident
        fields = [
            'estado', 'prioridad', 'categoria', 'assigned_to', 'created_by',
            'fecha_deteccion_from', 'fecha_deteccion_to',
            'created_at_from', 'created_at_to', 'cliente', 'provider', 'obra',
            'sku', 'lote', 'search'
        ]
    
    def filter_search(self, queryset, name, value):
        """General search across multiple fields"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(code__icontains=value) |
            Q(cliente__icontains=value) |
            Q(provider__icontains=value) |
            Q(obra__icontains=value) |
            Q(sku__icontains=value) |
            Q(lote__icontains=value) |
            Q(descripcion__icontains=value)
        )
