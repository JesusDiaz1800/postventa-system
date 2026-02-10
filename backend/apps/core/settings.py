"""
Unified, production-ready, and secure Django settings for the Postventa System.
This is the single source of truth for project configuration.
All sensitive values and environment-specific settings are controlled by environment variables.
"""
import os
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse, parse_qs, unquote

# --- Core Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- Environment Variables ---
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- Security ---
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'insecure-default-key-for-development-only')

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,testserver,*').split(',')

if not DEBUG:
    # Production Security Settings
    SECURE_SSL_REDIRECT = False # Set to True if using HTTPS
    SESSION_COOKIE_SECURE = False # Set to True if using HTTPS
    CSRF_COOKIE_SECURE = False # Set to True if using HTTPS
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

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
    'rest_framework_simplejwt.token_blacklist',
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
    'apps.integrations',
    'apps.notifications',
    'apps.audit',
    'apps.ai',
    'apps.ai_orchestrator',
    'apps.ai_agents',  # NEW: LangGraph-style multi-step reasoning agents
    'apps.sap_integration',
    'apps.reports',
    'apps.dashboard',
    # 'apps.advanced_reports',
    # 'apps.backup',
    # 'apps.monitoring',
]


INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

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
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'apps.audit.navigation_middleware.NavigationAuditMiddleware', # Desactivado para evitar logs basura
    # 'apps.audit.middleware.AuditMiddleware', # Desactivado: Causa logs duplicados y genéricos. Usamos signals.py
]

# --- URLs and Templates ---
ROOT_URLCONF = 'postventa_system.urls'
WSGI_APPLICATION = 'postventa_system.wsgi.application'
ASGI_APPLICATION = 'postventa_system.asgi.application'

# --- Django Channels (WebSocket) ---
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

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
def _build_database_config_from_env():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        parsed = urlparse(database_url)
        db_user = unquote(parsed.username) if parsed.username else os.getenv('DB_USER')
        db_password = unquote(parsed.password) if parsed.password else os.getenv('DB_PASSWORD')
        host = parsed.hostname or os.getenv('DB_HOST', 'localhost\\SQLEXPRESS')
        name = parsed.path.lstrip('/') if parsed.path else os.getenv('DB_NAME', 'postventa_system')
        q = parse_qs(parsed.query)
        driver = q.get('driver', [os.getenv('ODBC_DRIVER', 'ODBC Driver 18 for SQL Server')])[0]

        extra_pairs = []
        for key, values in q.items():
            if key.lower() == 'driver': continue
            extra_pairs.append(f"{key}={values[0]}")
        
        if not any(p.lower().startswith('encrypt=') for p in extra_pairs):
            extra_pairs.append('Encrypt=yes')
        if not any(p.lower().startswith('trustservercertificate=') for p in extra_pairs):
            extra_pairs.append('TrustServerCertificate=yes')
        if (not db_user) and (not db_password) and not any(p.lower().startswith('trusted_connection=') for p in extra_pairs):
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

DATABASES = {
    'default': _build_database_config_from_env(),
    'sap_db': {
        'ENGINE': 'mssql',
        'NAME': 'PRDPOLIFUSION',  # Base de datos de PRODUCCIÓN
        'USER': 'ccalidad',
        'PASSWORD': 'Plf2025**',
        'HOST': os.getenv('DB_HOST', 'localhost\\SQLEXPRESS'),
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 13 for SQL Server',
            'extra_params': 'Encrypt=no;TrustServerCertificate=yes;ApplicationIntent=ReadOnly;'  # READ ONLY
        },
    }
}

DATABASE_ROUTERS = ['apps.sap_integration.routers.SapRouter']

# --- Caching, Channels ---
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
CHANNEL_LAYERS = {
    "default": { "BACKEND": "channels.layers.InMemoryChannelLayer" },
}

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')

# --- Email Configuration (Office 365) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.office365.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')  # Tu correo de Office 365
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # Contraseña o App Password
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Santiago'
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Static and Media ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'documentos')
MEDIA_URL = '/documentos/'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- CORS / CSRF ---
# CORS_ALLOW_ALL_ORIGINS = True  # For dev simplicity - DISABLED FOR PRODUCTION
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only enable for dev/LAN if needed, otherwise rely on whitelist
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://localhost:5173", "http://127.0.0.1:5173",
    "https://localhost:5173", "https://127.0.0.1:5173",
    os.getenv('FRONTEND_URL', 'http://localhost:3000'),
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost", "http://127.0.0.1",
    "http://localhost:5173", "http://127.0.0.1:5173",
    "https://localhost:5173", "https://127.0.0.1:5173",
    os.getenv('FRONTEND_URL', 'http://localhost:3000'),
]

# Allow any 192.168.x.x origin for LAN development
import re
CORS_ORIGIN_REGEX_WHITELIST = [
    r"^https?://192\.168\.\d+\.\d+(:\d+)?$",
    r"^https?://localhost(:\d+)?$",
    r"^https?://postventa\.local(:\d+)?$",
]
CSRF_COOKIE_DOMAIN = None  # Allow cookies for any domain

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardResultsSetPagination',
    # 'PAGE_SIZE': 20, # Defined in pagination class
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend', 'rest_framework.filters.SearchFilter', 'rest_framework.filters.OrderingFilter',),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Postventa System API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler',},
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'postventa.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 2,
        },
    },
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
    },
}

SHARED_DOCUMENTS_PATH = os.getenv('SHARED_DOCUMENTS_PATH', os.path.join(BASE_DIR, 'shared'))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# --- AI Model Configurations ---
AI_OPENAI_MODEL = os.getenv('AI_OPENAI_MODEL', 'gpt-4o')
AI_ANTHROPIC_MODEL = os.getenv('AI_ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620')
AI_GOOGLE_MODEL = os.getenv('AI_GOOGLE_MODEL', 'gemini-1.5-flash')

# Suppress Google API key warning
import warnings
warnings.filterwarnings('ignore', message='.*GOOGLE_API_KEY.*')
warnings.filterwarnings('ignore', message='.*GEMINI_API_KEY.*')

os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
