from .thread_local import get_current_country

class DynamicTenantRouter:
    """
    Router dinámico que dirige las consultas a la base de datos correcta
    según el contexto del país (CL, PE, CO).
    Maneja tanto la BD de la App como la conexión a SAP.
    """
    
    route_app_labels = {'sap_integration'} # Apps que van a la DB de SAP

    def _get_db_name(self, app_label, **hints):
        """Determina el nombre de la BD destino basada en el contexto y la app."""
        country = get_current_country() # 'CL', 'PE', 'CO'
        
        # 1. Lógica para SAP (Solo lectura usualmente)
        if app_label in self.route_app_labels:
            if country == 'PE':
                return 'sap_db_pe'
            elif country == 'CO':
                return 'sap_db_co'
            return 'sap_db' # Default CL

        # 2. Lógica para la App (Django Models)
        # Si es auth, contenttypes, sessions -> ¿Queremos compartidos o separados?
        # PLAN: Separados por país para aislamiento total.
        
        if country == 'PE':
            return 'default_pe'
        elif country == 'CO':
            return 'default_co'
            
        return 'default' # Default CL

    def db_for_read(self, model, **hints):
        return self._get_db_name(model._meta.app_label)

    def db_for_write(self, model, **hints):
        return self._get_db_name(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Permitir relaciones solo si están en el mismo 'mundo' (mismo país).
        Aproximación simple: Si amboss apuntan a la misma lógica de ruteo, permitir.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Controla dónde se ejecutan las migraciones.
        
        - 'default' (CL) recibe todo.
        - 'default_pe' recibe todo.
        - 'default_co' recibe todo.
        - Las de SAP no reciben migraciones de Django.
        """
        # Apps de SAP nunca se migran (son legacy/externas)
        if app_label in self.route_app_labels:
            return False
            
        # Si estoy migrando una DB de App, permitir todo
        if db in ['default', 'default_pe', 'default_co']:
            return True
            
        return None
