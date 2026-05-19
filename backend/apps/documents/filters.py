import django_filters
from django.db.models import Q
from .models import Document


class DocumentFilter(django_filters.FilterSet):
    """Filter for documents"""
    
    # Document type filter
    document_type = django_filters.ChoiceFilter(
        choices=Document.DOCUMENT_TYPE_CHOICES,
        help_text='Tipo de documento'
    )
    
    # Incident filter
    incident = django_filters.NumberFilter(
        field_name='incident',
        help_text='ID de la incidencia'
    )
    
    incident_code = django_filters.CharFilter(
        field_name='incident__code',
        lookup_expr='icontains',
        help_text='Código de la incidencia'
    )
    
    # Status filter
    is_final = django_filters.BooleanFilter(
        field_name='is_final',
        help_text='Documento final'
    )
    
    # Date filters
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
    
    # Text search
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Búsqueda general en título y contenido'
    )
    
    # Creator filter
    created_by = django_filters.NumberFilter(
        field_name='created_by',
        help_text='ID del usuario que creó el documento'
    )
    
    class Meta:
        model = Document
        fields = [
            'document_type', 'incident', 'incident_code', 'is_final',
            'created_at_from', 'created_at_to', 'search', 'created_by'
        ]
    
    def filter_search(self, queryset, name, value):
        """General search across multiple fields"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) |
            Q(notes__icontains=value) |
            Q(incident__code__icontains=value) |
            Q(incident__cliente__icontains=value) |
            Q(incident__provider__icontains=value)
        )
