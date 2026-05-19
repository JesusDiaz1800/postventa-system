from asgiref.local import Local

_thread_locals = Local()

def set_current_country(country_code):
    """Establece el código de país para el contexto actual (Hilo o Corrutina)."""
    _thread_locals.country_code = country_code

def get_current_country():
    """Obtiene el código de país del contexto actual. Default: 'CL'."""
    return getattr(_thread_locals, 'country_code', 'CL')

def clear_current_country():
    """Limpia el contexto del país."""
    if hasattr(_thread_locals, 'country_code'):
        delattr(_thread_locals, 'country_code')

def set_current_user(user):
    """Establece el usuario actual para auditoría."""
    _thread_locals.user = user

def get_current_user():
    """Obtiene el usuario actual."""
    return getattr(_thread_locals, 'user', None)

def clear_current_user():
    """Limpia el usuario del contexto actual."""
    if hasattr(_thread_locals, 'user'):
        delattr(_thread_locals, 'user')
