"""
Django settings for postventa_system project with SQL Server and shared folder.
"""

import os
from pathlib import Path
try:
    import environ
except ImportError:
    environ = None

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-change-this-in-production'),
    DATABASE_URL=(str, 'mssql://sa:TuPassword123!@localhost:1433/postventa_system'),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
    SHARED_DOCUMENTS_PATH=(str, 'Y:\\CONTROL DE CALIDAD\\postventa'),
    OPENAI_API_KEY=(str, ''),
    ANTHROPIC_API_KEY=(str, ''),
    GOOGLE_API_KEY=(str, ''),
    GEMINI_API_KEY=(str, ''),
)

# Read .env file
# environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Forzar modo desarrollo para pruebas de email

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Application definition
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
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.users',
    'apps.incidents',
    'apps.documents',
    'apps.ai',
    'apps.ai_orchestrator',
    'apps.audit',
    'apps.workflows',
    'apps.reports',
    'apps.dashboard',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'apps.users.middleware.APIPermissionMiddleware',  # Deshabilitado temporalmente
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.audit.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'postventa_system.urls'

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

WSGI_APPLICATION = 'postventa_system.wsgi.application'

# SQL Server Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': env('DB_NAME', default='postventa_system'),
        'USER': env('DB_USER', default=''),  # Empty for Windows Authentication
        'PASSWORD': env('DB_PASSWORD', default=''),  # Empty for Windows Authentication
        'HOST': env('DB_HOST', default='NB-JDIAZ25\\SQLEXPRESS'),
        'PORT': env('DB_PORT', default=''),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'Server=NB-JDIAZ25\\SQLEXPRESS;Database=postventa_system;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;',
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files - Using local media folder for uploads
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Shared documents path (Empresa)
SHARED_DOCUMENTS_PATH = r"Y:\CONTROL DE CALIDAD\postventa"

# Create shared folder structure if it doesn't exist
def create_shared_folder_structure():
    """Create folder structure in shared location"""
    folders = [
        'documents',
        'images',
        'templates',
        'temp',
        'backups'
    ]
    
    for folder in folders:
        folder_path = os.path.join(SHARED_DOCUMENTS_PATH, folder)
        os.makedirs(folder_path, exist_ok=True)

# Create folders on startup
try:
    create_shared_folder_structure()
except Exception as e:
    print(f"Warning: Could not create shared folder structure: {e}")

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Permitir acceso desde cualquier origen en desarrollo (cambiar en producción)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Headers adicionales permitidos
CORS_ALLOW_HEADERS = [
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

# Celery Configuration
CELERY_BROKER_URL = env('REDIS_URL')
CELERY_RESULT_BACKEND = env('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# AI Providers Configuration
AI_PROVIDERS = {
    'openai': {
        'api_key': env('OPENAI_API_KEY'),
        'enabled': bool(env('OPENAI_API_KEY')),
        'daily_quota_tokens': 100000,
        'daily_quota_calls': 1000,
        'priority': 1,
    },
    'anthropic': {
        'api_key': env('ANTHROPIC_API_KEY'),
        'enabled': bool(env('ANTHROPIC_API_KEY')),
        'daily_quota_tokens': 100000,
        'daily_quota_calls': 1000,
        'priority': 2,
    },
    'google': {
        'api_key': env('GOOGLE_API_KEY'),
        'enabled': bool(env('GOOGLE_API_KEY')),
        'daily_quota_tokens': 100000,
        'daily_quota_calls': 1000,
        'priority': 3,
    },
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Postventa System API',
    'DESCRIPTION': 'API for Post-Sales Incident Management System',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# AI Services Configuration
GEMINI_API_KEY = env('GEMINI_API_KEY')

# Email Configuration
if DEBUG:
    # En modo desarrollo, usar backend de consola para pruebas
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    print("Modo desarrollo: Los emails se mostraran en la consola")
else:
    # En producción, usar SMTP real
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'postventa@polifusion.cl'  # Cambiar por el email real
    EMAIL_HOST_PASSWORD = 'TuPassword123!'  # Cambiar por la contraseña real
    DEFAULT_FROM_EMAIL = 'postventa@polifusion.cl'
