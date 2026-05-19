import unicodedata
from rest_framework.filters import SearchFilter

def normalize_text(text):
    """
    Normaliza una cadena para búsqueda:
    - Quita acentos.
    - Convierte a minúsculas.
    - Colapsa espacios.
    """
    if not text:
        return ""
    
    # Normalizar NFD para separar acentos
    text = unicodedata.normalize('NFD', text)
    # Filtrar caracteres que no sean diacríticos y unir
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # Lowercase, trim y colapsar espacios
    return " ".join(text.lower().split())

class SmartSearchFilter(SearchFilter):
    """
    Filtro de búsqueda inteligente que normaliza el término de búsqueda
    (quita acentos y espacios extra) antes de realizar la consulta.
    """
    def get_search_terms(self, request):
        """
        Sobrescribimos para normalizar los términos que vienen del cliente.
        """
        params = request.query_params.get(self.search_param, '')
        params = params.replace('\x00', '')  # Eliminar caracteres nulos
        
        # Normalizamos el término completo antes de dividir por comas/espacios
        normalized_params = normalize_text(params)
        
        if normalized_params:
            return normalized_params.split()
        return []
