"""
Configuración para deployment empresarial
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'servidor-empresa',  # Cambiar por el nombre de tu servidor
    'servidor-empresa.local',  # Si usas dominio local
    '192.168.1.100',  # IP del servidor
    # Agregar más hosts según sea necesario
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'apps.incidents',
    'apps.users',
    'apps.documents',
    'apps.audit',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'postventa_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# Database - SQL Server para empresa
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'postventa_empresa',
        'USER': 'sa',
        'PASSWORD': 'TuPasswordSeguro123!',
        'HOST': 'localhost',  # O IP del servidor de BD
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==================== CONFIGURACIÓN EMPRESARIAL ====================

# Carpeta compartida de red para documentos
# OPCIÓN 1: Carpeta compartida de red (RECOMENDADA)
SHARED_DOCUMENTS_PATH = r'\\servidor-empresa\documentos'

# OPCIÓN 2: Unidad mapeada
# SHARED_DOCUMENTS_PATH = r'Z:\documentos'

# OPCIÓN 3: Carpeta local (solo para desarrollo)
# SHARED_DOCUMENTS_PATH = r'C:\Documentos'

# Configuración de email empresarial
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.empresa.com'  # Cambiar por tu servidor SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sistema@empresa.com'
EMAIL_HOST_PASSWORD = 'password_email'
DEFAULT_FROM_EMAIL = 'Sistema Postventa <sistema@empresa.com>'

# Configuración de logging empresarial
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'postventa.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Configuración de seguridad empresarial
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS para acceso desde diferentes ubicaciones
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://servidor-empresa",  # Cambiar por tu servidor
    "https://servidor-empresa.com",  # Si usas HTTPS
]

# Configuración de sesiones empresariales
SESSION_COOKIE_AGE = 28800  # 8 horas
SESSION_COOKIE_SECURE = True  # Solo HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Configuración de archivos estáticos para producción
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración de archivos de media para producción
MEDIAFILES_DIRS = [
    os.path.join(BASE_DIR, 'media'),
]

# ==================== CONFIGURACIÓN DE BACKUP ====================

# Configuración de backup automático
BACKUP_CONFIG = {
    'enabled': True,
    'schedule': 'daily',  # daily, weekly, monthly
    'retention_days': 30,
    'backup_path': r'\\backup-servidor\postventa',  # Cambiar por tu servidor de backup
    'include_database': True,
    'include_media': True,
    'include_documents': True,
}

# ==================== CONFIGURACIÓN DE MONITOREO ====================

# Configuración de monitoreo del sistema
MONITORING_CONFIG = {
    'enabled': True,
    'check_interval': 300,  # 5 minutos
    'alert_email': 'admin@empresa.com',
    'disk_threshold': 90,  # Porcentaje de uso de disco
    'memory_threshold': 85,  # Porcentaje de uso de memoria
}

# ==================== CONFIGURACIÓN DE USUARIOS ====================

# Configuración de roles empresariales
USER_ROLES = {
    'admin': {
        'permissions': ['view_all', 'edit_all', 'delete_all', 'manage_users'],
        'description': 'Administrador del sistema'
    },
    'supervisor': {
        'permissions': ['view_all', 'edit_assigned', 'manage_team'],
        'description': 'Supervisor de área'
    },
    'tecnico': {
        'permissions': ['view_assigned', 'upload_documents', 'edit_own'],
        'description': 'Técnico de campo'
    },
    'cliente': {
        'permissions': ['view_own', 'upload_own'],
        'description': 'Cliente externo'
    }
}

# Configuración de autenticación empresarial
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # Descomentar si usas Active Directory
    # 'django_auth_ldap.backend.LDAPBackend',
]

# ==================== CONFIGURACIÓN DE NOTIFICACIONES ====================

# Configuración de notificaciones empresariales
NOTIFICATION_CONFIG = {
    'email_notifications': True,
    'sms_notifications': False,  # Configurar si tienes servicio SMS
    'push_notifications': False,  # Para futuras implementaciones
    'notification_recipients': {
        'new_incident': ['admin@empresa.com', 'supervisor@empresa.com'],
        'incident_escalated': ['admin@empresa.com'],
        'incident_closed': ['cliente@empresa.com'],
    }
}

# ==================== CONFIGURACIÓN DE REPORTES ====================

# Configuración de reportes empresariales
REPORTING_CONFIG = {
    'default_format': 'pdf',
    'email_reports': True,
    'schedule_reports': True,
    'report_recipients': {
        'daily': ['admin@empresa.com'],
        'weekly': ['admin@empresa.com', 'supervisor@empresa.com'],
        'monthly': ['admin@empresa.com', 'gerencia@empresa.com'],
    }
}

# ==================== CONFIGURACIÓN DE INTEGRACIÓN ====================

# Configuración de integración con sistemas empresariales
INTEGRATION_CONFIG = {
    'erp_integration': False,  # Integración con ERP
    'crm_integration': False,  # Integración con CRM
    'accounting_integration': False,  # Integración con contabilidad
    'api_endpoints': {
        'external_api_url': 'https://api.empresa.com',
        'api_key': 'tu_api_key_aqui',
        'timeout': 30,
    }
}

# ==================== CONFIGURACIÓN DE DESARROLLO ====================

# Configuración específica para desarrollo
if DEBUG:
    # Configuración de desarrollo
    SHARED_DOCUMENTS_PATH = os.path.join(BASE_DIR, 'shared_documents')
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    LOGGING['handlers']['console']['level'] = 'DEBUG'
    LOGGING['root']['level'] = 'DEBUG'
