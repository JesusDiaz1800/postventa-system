"""
Unified, production-ready, and secure Django settings for the Postventa System.
This is the single source of truth for project configuration.
All sensitive values and environment-specific settings are controlled by environment variables.
"""
import os
from pathlib import Path
from datetime import timedelta

# --- Core Paths ---
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Environment Variables ---
# Load environment variables from .env file if it exists
# In a production environment, these variables should be set directly.
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, 'backend', '.env'))

# --- Security ---
# DEBUG should be False in production.
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# The SECRET_KEY must be set in the environment for production.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'insecure-default-key-for-development-only')

# Define allowed hosts via environment variable, comma-separated.
<<<<<<< HEAD
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,192.168.1.234').split(',')
=======
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,192.168.1.234,testserver').split(',')
>>>>>>> 674c244 (tus cambios)


# --- Application Definition ---
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.users',
    'apps.incidents',
    'apps.documents',
    'apps.audit',
    'apps.dashboard',
    'apps.notifications',
    'apps.reports',
    'apps.ai',
    'apps.ai_orchestrator',
    'apps.workflows',
    'apps.integrations',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

<<<<<<< HEAD
=======
# Agregar rest_framework_simplejwt.token_blacklist para logout
if 'rest_framework_simplejwt.token_blacklist' not in THIRD_PARTY_APPS:
    THIRD_PARTY_APPS.append('rest_framework_simplejwt.token_blacklist')

>>>>>>> 674c244 (tus cambios)

# --- Middleware ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
<<<<<<< HEAD
    'apps.audit.middleware.AuditMiddleware',
=======
    'apps.audit.navigation_middleware.NavigationAuditMiddleware',  # Registrar navegación
    'apps.audit.middleware.AuditMiddleware',  # Registrar acciones importantes
>>>>>>> 674c244 (tus cambios)
]


# --- URLs and Templates ---
ROOT_URLCONF = 'postventa_system.urls'
WSGI_APPLICATION = 'postventa_system.wsgi.application'
ASGI_APPLICATION = 'postventa_system.asgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# --- Database ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Permite configuración vía variables discretas (DB_*) o un DATABASE_URL estilo mssql+pyodbc
def _build_database_config_from_env():
    from urllib.parse import urlparse, parse_qs, unquote

    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Esperado: mssql+pyodbc://USER:PASSWORD@HOST\\INSTANCE/NAME?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
        parsed = urlparse(database_url)
        # Usuario/clave
        db_user = unquote(parsed.username) if parsed.username else os.getenv('DB_USER')
        db_password = unquote(parsed.password) if parsed.password else os.getenv('DB_PASSWORD')
        # Host puede incluir instancia con backslash
        host = parsed.hostname or os.getenv('DB_HOST', 'localhost\\SQLEXPRESS')
        # Nombre base de datos
        name = parsed.path.lstrip('/') if parsed.path else os.getenv('DB_NAME', 'postventa_system')
        # Parámetros de conexión
        q = parse_qs(parsed.query)
        driver = q.get('driver', [os.getenv('ODBC_DRIVER', 'ODBC Driver 18 for SQL Server')])[0]

        # Construir extra_params desde el query string manteniendo mayúsculas/minúsculas en claves críticas
        # y preservando valores con espacios.
        extra_pairs = []
        for key, values in q.items():
            if key.lower() == 'driver':
                continue
            # Tomar el primer valor
            value = values[0]
            extra_pairs.append(f"{key}={value}")
        # Valores por defecto seguros si no vienen en la URL
        if not any(p.lower().startswith('encrypt=') for p in extra_pairs):
            extra_pairs.append('Encrypt=yes')
        if not any(p.lower().startswith('trustservercertificate=') for p in extra_pairs):
            extra_pairs.append('TrustServerCertificate=yes')
        if (not db_user) and (not db_password) and not any(p.lower().startswith('trusted_connection=') for p in extra_pairs):
            # Si no hay usuario/clave, asumir autenticación integrada de Windows
            extra_pairs.append('Trusted_Connection=yes')
        extra_params = ';'.join(extra_pairs) + (';' if extra_pairs else '')

        return {
            'ENGINE': 'mssql',
            'NAME': name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': host,
            'PORT': os.getenv('DB_PORT', ''),
            'OPTIONS': {
                'driver': driver,
                'extra_params': extra_params or os.getenv('DB_EXTRA_PARAMS', 'Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;')
            },
        }

    # Fallback: variables discretas
    return {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME', 'postventa_system'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost\\SQLEXPRESS'),
        'PORT': os.getenv('DB_PORT', ''),
        'OPTIONS': {
            'driver': os.getenv('ODBC_DRIVER', 'ODBC Driver 18 for SQL Server'),
            'extra_params': os.getenv('DB_EXTRA_PARAMS', 'Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;')
        },
    }

<<<<<<< HEAD
DATABASES = {
    'default': _build_database_config_from_env()
}

=======
# Configuración SQL Server Express (producción interna)
# Host de tu PC: NB-JDIAZ25 (IP 192.168.1.165)
# Se usa puerto fijo 1433 para asegurar acceso remoto; todo se puede sobrescribir por variables de entorno.
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME', 'postventa_system'),
        'USER': os.getenv('DB_USER', 'postventa_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Postventa2025!'),
        # Host/IP y puerto explícitos; se pueden cambiar por env DB_HOST y DB_PORT
        'HOST': os.getenv('DB_HOST', '192.168.1.165'),
        'PORT': os.getenv('DB_PORT', '1433'),
        'OPTIONS': {
            'driver': os.getenv('ODBC_DRIVER', 'ODBC Driver 13 for SQL Server'),
            'extra_params': os.getenv('DB_EXTRA_PARAMS', 'Encrypt=no;TrustServerCertificate=yes;')
        },
    }
}

# Configuración SQL Server Express Remoto (pendiente configuración)
# Para habilitar conexión remota necesitas:
# 1. Habilitar conexiones remotas en SQL Server Configuration Manager
# 2. Configurar autenticación SQL Server (no Windows)
# 3. Abrir puerto 1433 en firewall
# 4. Crear usuario SQL Server con permisos
# DATABASES = {
#     'default': {
#         'ENGINE': 'mssql',
#         'NAME': 'postventa_system',
#         'USER': 'postventa_user',
#         'PASSWORD': 'postventa_password',
#         'HOST': '192.168.1.125',
#         'PORT': '1433',
#         'OPTIONS': {
#             'driver': 'ODBC Driver 17 for SQL Server',
#             'extra_params': 'Encrypt=yes;TrustServerCertificate=yes;'
#         },
#     }
# }

# Configuración SQL Server empresarial (pendiente datos de TI)
# DATABASES = {
#     'default': {
#         'ENGINE': 'mssql',
#         'NAME': 'PostventaDB',
#         'USER': '[USUARIO_PROVIDIDO_POR_TI]',
#         'PASSWORD': '[CONTRASEÑA_PROVIDIDA_POR_TI]',
#         'HOST': '[SERVIDOR_PROVIDIDO_POR_TI]',
#         'PORT': '1433',
#         'OPTIONS': {
#             'driver': 'ODBC Driver 17 for SQL Server',
#             'TrustServerCertificate': 'yes',
#             'extra_params': 'Encrypt=no;'
#         },
#     }
# }

>>>>>>> 674c244 (tus cambios)

# --- Caching, Channels, and Celery ---
# Using Redis for production, with simpler fallbacks for local development.
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

if DEBUG:
    # Development settings: simple and file-based
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    CHANNEL_LAYERS = {
        "default": { "BACKEND": "channels.layers.InMemoryChannelLayer" },
    }
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
<<<<<<< HEAD
    # Production settings: robust and scalable with Redis
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
            "OPTIONS": { "CLIENT_CLASS": "django_redis.client.DefaultClient" }
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": { "hosts": [(REDIS_HOST, int(REDIS_PORT))] },
        },
=======
    # Production settings: using in-memory cache for now (Redis not available)
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }
    CHANNEL_LAYERS = {
        "default": { "BACKEND": "channels.layers.InMemoryChannelLayer" },
>>>>>>> 674c244 (tus cambios)
    }
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Celery shared settings
CELERY_RESULT_BACKEND = 'django-db' # Using django-db for results is fine
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Santiago'


# --- Authentication and Authorization ---
AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization ---
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True


# --- Defaults and production safety checks ---
# Use BigAutoField by default to avoid AutoField warnings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Enforce a secure SECRET_KEY when running in an explicit production environment.
# This avoids blocking local developer tasks when DEBUG is False but the environment
# isn't actually production. To force enforcement, set DJANGO_ENV=production or
# ENFORCE_SECRET_KEY=1 in the environment.
ENVIRONMENT = os.getenv('DJANGO_ENV', 'development')
if ENVIRONMENT.lower() == 'production' or os.getenv('ENFORCE_SECRET_KEY', '') == '1':
    # The default development placeholder is insecure; require a proper key.
    insecure_prefixes = ('insecure', 'django-insecure-')
    if (not SECRET_KEY) or len(SECRET_KEY) < 50 or SECRET_KEY.startswith(insecure_prefixes):
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY must be set to a long, random value in production. '
            'Generate one (e.g. using `openssl rand -base64 48`) and set the DJANGO_SECRET_KEY environment variable.'
        )


# --- Static and Media Files ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Gestión centralizada de documentos
MEDIA_ROOT = os.path.join(BASE_DIR, 'documentos')
MEDIA_URL = '/documentos/'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- CORS / CSRF / Proxy ---
<<<<<<< HEAD
CORS_ALLOWED_ORIGINS = os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# Permitir CSRF desde orígenes confiables (requerido cuando se usa HTTPS o dominios externos)
CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1').split(',')
=======
CORS_ALLOWED_ORIGINS = os.getenv('DJANGO_CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000,http://192.168.1.234:3000,http://localhost:5173,http://127.0.0.1:5173,http://192.168.1.234:5173').split(',')
CORS_ALLOW_CREDENTIALS = True

# Permitir CSRF desde orígenes confiables (requerido cuando se usa HTTPS o dominios externos)
CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', 'http://localhost,http://127.0.0.1,http://192.168.1.234').split(',')
>>>>>>> 674c244 (tus cambios)

# Si está detrás de un proxy (Nginx/Traefik) con TLS, honrar cabeceras proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if os.getenv('USE_SECURE_PROXY', 'True') == 'True' else None
USE_X_FORWARDED_HOST = True if os.getenv('USE_X_FORWARDED_HOST', 'True') == 'True' else False


# --- Django REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
}

# --- Simple JWT ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# --- API Documentation (drf-spectacular) ---
SPECTACULAR_SETTINGS = {
    'TITLE': 'Postventa System API',
    'DESCRIPTION': 'API for Post-Sales Incident Management System',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# --- Logging ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'postventa.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 2,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# --- Custom Application Settings ---
# These are settings specific to your application's logic.
# They are controlled by environment variables for flexibility.
SHARED_DOCUMENTS_PATH = os.getenv('SHARED_DOCUMENTS_PATH', os.path.join(BASE_DIR, 'shared'))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# --- Production Security Settings ---
# These are activated when DEBUG is False.
if not DEBUG:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
<<<<<<< HEAD
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'
=======
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'
>>>>>>> 674c244 (tus cambios)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', 31536000)) # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True') == 'True'
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'True') == 'True'
<<<<<<< HEAD
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
=======
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# Configuracion CORS para acceso desde otros PCs
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.234:5173",
]

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
>>>>>>> 674c244 (tus cambios)
