"""
Configuraciones de seguridad mejoradas para el sistema Postventa
"""

import os
from django.conf import settings

# Configuraciones de seguridad para producción
SECURITY_SETTINGS = {
    # Headers de seguridad
    'SECURE_BROWSER_XSS_FILTER': True,
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'X_FRAME_OPTIONS': 'DENY',
    'SECURE_HSTS_SECONDS': 31536000,  # 1 año
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_HSTS_PRELOAD': True,
    
    # Cookies seguras
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Strict',
    'CSRF_COOKIE_SECURE': True,
    'CSRF_COOKIE_HTTPONLY': True,
    'CSRF_COOKIE_SAMESITE': 'Strict',
    
    # SSL/TLS
    'SECURE_SSL_REDIRECT': True,
    'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
    
    # Rate limiting
    'RATELIMIT_ENABLE': True,
    'RATELIMIT_USE_CACHE': 'default',
    'RATELIMIT_VIEW': 'django_ratelimit.views.RatelimitView',
    
    # Logging de seguridad
    'SECURITY_LOGGING': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'security': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'security_file': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': os.path.join(settings.BASE_DIR, 'logs', 'security.log'),
                'formatter': 'security',
            },
        },
        'loggers': {
            'django.security': {
                'handlers': ['security_file'],
                'level': 'WARNING',
                'propagate': False,
            },
        },
    },
}

# Configuraciones de autenticación mejoradas
AUTH_SECURITY_SETTINGS = {
    # Límites de intentos de login
    'LOGIN_ATTEMPT_LIMIT': 5,
    'LOGIN_ATTEMPT_TIMEOUT': 300,  # 5 minutos
    
    # Expiración de sesiones
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': True,
    'SESSION_COOKIE_AGE': 28800,  # 8 horas
    
    # JWT mejorado
    'JWT_SECURITY': {
        'ACCESS_TOKEN_LIFETIME': 3600,  # 1 hora
        'REFRESH_TOKEN_LIFETIME': 604800,  # 7 días
        'ROTATE_REFRESH_TOKENS': True,
        'BLACKLIST_AFTER_ROTATION': True,
        'ALGORITHM': 'HS256',
        'AUTH_HEADER_TYPES': ('Bearer',),
    },
    
    # Validación de contraseñas
    'PASSWORD_VALIDATION': {
        'MIN_LENGTH': 12,
        'REQUIRE_UPPERCASE': True,
        'REQUIRE_LOWERCASE': True,
        'REQUIRE_NUMBERS': True,
        'REQUIRE_SYMBOLS': True,
        'FORBID_COMMON_PASSWORDS': True,
        'FORBID_USER_ATTRIBUTES': True,
    },
}

# Configuraciones de API
API_SECURITY_SETTINGS = {
    # Rate limiting por endpoint
    'RATE_LIMITS': {
        'login': '5/m',  # 5 intentos por minuto
        'api': '100/h',  # 100 requests por hora
        'upload': '10/h',  # 10 uploads por hora
        'ai_analysis': '50/d',  # 50 análisis por día
    },
    
    # Validación de entrada
    'INPUT_VALIDATION': {
        'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
        'ALLOWED_FILE_TYPES': ['.jpg', '.jpeg', '.png', '.pdf', '.docx', '.xlsx'],
        'MAX_STRING_LENGTH': 10000,
        'SANITIZE_HTML': True,
    },
    
    # CORS mejorado
    'CORS_SECURITY': {
        'ALLOWED_ORIGINS': [
            'https://localhost:3000',
            'https://192.168.1.161:3000',
        ],
        'ALLOW_CREDENTIALS': True,
        'ALLOWED_HEADERS': [
            'accept',
            'accept-encoding',
            'authorization',
            'content-type',
            'dnt',
            'origin',
            'user-agent',
            'x-csrftoken',
            'x-requested-with',
        ],
    },
}

# Configuraciones de base de datos
DATABASE_SECURITY_SETTINGS = {
    # Conexión segura
    'CONNECTION_SECURITY': {
        'ENCRYPT': True,
        'TRUST_SERVER_CERTIFICATE': False,
        'CONNECTION_TIMEOUT': 30,
        'COMMAND_TIMEOUT': 60,
    },
    
    # Backup automático
    'BACKUP_SETTINGS': {
        'ENABLED': True,
        'FREQUENCY': 'daily',  # daily, weekly, monthly
        'RETENTION_DAYS': 30,
        'BACKUP_PATH': '/backups/postventa',
        'COMPRESSION': True,
    },
    
    # Auditoría de base de datos
    'AUDIT_SETTINGS': {
        'ENABLED': True,
        'LOG_ALL_QUERIES': False,
        'LOG_SLOW_QUERIES': True,
        'SLOW_QUERY_THRESHOLD': 1000,  # ms
    },
}

# Configuraciones de logging de seguridad
SECURITY_LOGGING_SETTINGS = {
    'LOG_FAILED_LOGINS': True,
    'LOG_PASSWORD_CHANGES': True,
    'LOG_PERMISSION_CHANGES': True,
    'LOG_DATA_ACCESS': True,
    'LOG_ADMIN_ACTIONS': True,
    'LOG_FILE_ROTATION': {
        'MAX_BYTES': 10 * 1024 * 1024,  # 10MB
        'BACKUP_COUNT': 5,
    },
}

# Función para aplicar configuraciones de seguridad
def apply_security_settings():
    """Aplica todas las configuraciones de seguridad"""
    import django.conf
    
    # Aplicar configuraciones de seguridad
    for key, value in SECURITY_SETTINGS.items():
        if key != 'SECURITY_LOGGING':  # Manejar logging por separado
            setattr(django.conf.settings, key, value)
    
    # Aplicar configuraciones de autenticación
    for key, value in AUTH_SECURITY_SETTINGS.items():
        setattr(django.conf.settings, key, value)
    
    # Aplicar configuraciones de API
    for key, value in API_SECURITY_SETTINGS.items():
        setattr(django.conf.settings, key, value)
    
    # Aplicar configuraciones de base de datos
    for key, value in DATABASE_SECURITY_SETTINGS.items():
        setattr(django.conf.settings, key, value)
    
    # Aplicar configuraciones de logging
    for key, value in SECURITY_LOGGING_SETTINGS.items():
        setattr(django.conf.settings, key, value)
    
    return True

# Middleware de seguridad personalizado
class SecurityMiddleware:
    """Middleware para aplicar configuraciones de seguridad adicionales"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Aplicar headers de seguridad
        response = self.get_response(request)
        
        # Headers de seguridad adicionales
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
