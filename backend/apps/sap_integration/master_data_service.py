import logging
from django.core.cache import cache
from apps.core.thread_local import get_current_country

logger = logging.getLogger(__name__)

class MasterDataService:
    """
    Servicio para manejar mapeos de datos maestros de SAP (ProblemTypes, etc.)
    Evita mostrar IDs numéricos ("1") en reportes y UI.
    """
    
    # Mapeos estáticos como fallback si falla la consulta o para velocidad
    # Basado en auditoría previa de los 3 países
    MAPPINGS = {
        'CL': {
            1: "01-Visita Tecnica",
            2: "Vtm",
            3: "02-Cap. Gral",
            4: "Aclarar Dudas",
            13: "17-Retirar Maq.Elec",
            16: "Ver Filtracion",
            18: "Revision Depto",
            20: "Consulta en Obra",
            33: "Post Venta",
        },
        'PE': {
            1: "INSTALACION",
            2: "REPARACION",
            3: "MANTENIMIENTO",
            13: "Post Venta",
        },
        'CO': {
            1: "Visita Técnica",
            2: "Reunión Técnica",
            3: "Revisión Calidad",
            33: "Post Venta",
        }
    }

    @classmethod
    def get_problem_type_name(cls, problem_id):
        """
        Retorna el nombre descriptivo del ProblemTypeID según el país.
        """
        if not problem_id:
            return "No especificado"
            
        try:
            problem_id = int(problem_id)
        except (ValueError, TypeError):
            return str(problem_id)
            
        country = get_current_country() or 'CL'
        country_mappings = cls.MAPPINGS.get(country, cls.MAPPINGS['CL'])
        
        name = country_mappings.get(problem_id)
        if name:
            return name
            
        # Intentar buscar en caché si se implementaran consultas dinámicas a futuro
        # Por ahora, retornar el ID si no hay mapeo
        return f"Motivo {problem_id}"

    @classmethod
    def get_all_for_country(cls, country=None):
        if not country:
            country = get_current_country() or 'CL'
        return cls.MAPPINGS.get(country, cls.MAPPINGS['CL'])
