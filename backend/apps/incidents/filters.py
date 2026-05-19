import django_filters
from django.db.models import Q
from .models import Incident, Category, Responsible


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
    
    categoria = django_filters.CharFilter(
        method='filter_categoria',
        help_text='Categoría o área funcional'
    )

    responsable = django_filters.CharFilter(
        method='filter_responsable',
        help_text='Responsable técnico'
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
    
    # Text search filters (con validación de vacío)
    cliente = django_filters.CharFilter(
        method='filter_by_field',
        help_text='Nombre del cliente'
    )
    
    provider = django_filters.CharFilter(
        method='filter_by_field',
        help_text='Proveedor'
    )
    
    obra = django_filters.CharFilter(
        method='filter_by_field',
        help_text='Obra o proyecto'
    )
    
    lote = django_filters.CharFilter(
        method='filter_by_field',
        help_text='Número de lote'
    )
    
    # Complex search
    search = django_filters.CharFilter(
        method='filter_search',
        help_text='Búsqueda general en código, cliente, obra, folio SAP, categoría, subcategoría y descripción'
    )
    
    class Meta:
        model = Incident
        fields = [
            'estado', 'prioridad', 'categoria', 'responsable', 'assigned_to', 'created_by',
            'fecha_deteccion_from', 'fecha_deteccion_to',
            'created_at_from', 'created_at_to', 'cliente', 'provider', 'obra',
            'lote', 'search'
        ]
    
    def filter_categoria(self, queryset, name, value):
        """Maneja IDs numéricos o nombres de categoría (slugs del frontend)"""
        if not value:
            return queryset
        if str(value).isdigit():
            return queryset.filter(categoria_id=value)
        # Si es texto, buscamos por nombre. Si no existe, no filtramos para no romper la vista
        # Esto maneja el caso de 'postventa', 'seguridad' que no existen como categorías
        qs = queryset.filter(categoria__name__icontains=value)
        if not qs.exists() and value in ['postventa', 'seguridad', 'calidad_interna', 'calidad_cliente']:
            return queryset # Ignorar filtros de áreas que no son categorías reales
        return qs

    def filter_responsable(self, queryset, name, value):
        """Maneja IDs numéricos o nombres de responsable"""
        if not value:
            return queryset
        if str(value).isdigit():
            return queryset.filter(responsable_id=value)
        return queryset.filter(responsable__name__icontains=value)

    def filter_by_field(self, queryset, name, value):
        """Evita filtrar por strings vacíos que rompen la búsqueda en SQL Server (campos NULL)"""
        if not value or value == '':
            return queryset
        return queryset.filter(**{f"{name}__icontains": value})

    def filter_search(self, queryset, name, value):
        """
        Búsqueda profesional por tokens:
        Divide la consulta en palabras y asegura que cada palabra coincida con al menos un campo.
        """
        if not value or value == '':
            return queryset
            
        tokens = value.split()
        if not tokens:
            return queryset
            
        # Aplicamos un filtro por cada token (AND entre palabras)
        for token in tokens:
            sap_filter = Q()
            if token.isdigit():
                sap_filter = Q(sap_doc_num__icontains=token) | Q(sap_call_id__icontains=token)
                
            queryset = queryset.filter(
                Q(code__icontains=token) |
                Q(cliente__icontains=token) |
                Q(cliente_rut__icontains=token) |
                Q(obra__icontains=token) |
                Q(provider__icontains=token) |
                Q(lote__icontains=token) |
                Q(descripcion__icontains=token) |
                Q(categoria__name__icontains=token) |
                Q(subcategoria__icontains=token) |
                sap_filter
            )
            
        return queryset.distinct()
