from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class UnifiedSearchMixin:
    """
    Mixin para unificar la lógica de búsqueda profesional en vistas basadas en queryset.
    Permite definir search_fields_map para búsquedas por tokens en múltiples campos.
    """
    search_fields_map = []
    default_select_related = []
    default_prefetch_related = []

    def get_optimized_queryset(self):
        """
        Retorna el queryset con select_related y prefetch_related aplicados.
        """
        queryset = self.model.objects.all()
        
        if self.default_select_related:
            queryset = queryset.select_related(*self.default_select_related)
        
        if self.default_prefetch_related:
            queryset = queryset.prefetch_related(*self.default_prefetch_related)
            
        return queryset

    def apply_search(self, queryset):
        """
        Aplica búsqueda por tokens sobre el queryset basado en search_fields_map.
        """
        search = self.request.query_params.get('search')
        if not search or not self.search_fields_map:
            return queryset

        tokens = search.split()
        for token in tokens:
            search_query = Q()
            for field in self.search_fields_map:
                search_query |= Q(**{f"{field}__icontains": token})
            queryset = queryset.filter(search_query)
        
        return queryset.distinct()
