from .thread_local import (
    set_current_country, clear_current_country,
    set_current_user, get_current_user, clear_current_user
)


class CsrfExemptAPIMiddleware:
    """
    Exime las rutas /api/ y /ws/ de la verificación CSRF de Django.
    Esto es seguro porque la API usa JWT (Bearer tokens), no cookies de sesión.
    CSRF solo protege contra ataques basados en cookies, que no aplican con JWT.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/') or request.path.startswith('/ws/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)


class TenantMiddleware:
    """
    Middleware para gestionar el contexto del país (Tenant) basado en el header 'X-Country-Code'.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Obtener país del header (Frontend envía: CL, PE, CO)
        country_code = request.headers.get('X-Country-Code', 'CL').upper()
        
        # LOG DEBUG: Ver que país estamos recibiendo
        import logging
        logger = logging.getLogger(__name__)
        if country_code != 'CL':
            logger.info(f"[TenantMiddleware] Country Context: {country_code}")
        
        # 2. Validar que sea un código soportado (Seguridad básica)
        if country_code not in ['CL', 'PE', 'CO']:
            country_code = 'CL' # Fallback seguro
            
        # 3. Establecer contexto en thread_local
        set_current_country(country_code)
        
        # 4. Establecer usuario en thread_local para auditoría
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        
        try:
            response = self.get_response(request)
        finally:
            # 5. Limpiar contexto al terminar el request
            clear_current_country()
            clear_current_user()
            
        return response