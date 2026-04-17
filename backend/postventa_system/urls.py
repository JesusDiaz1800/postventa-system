"""
URL configuration for postventa_system project.
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenRefreshView

from django.views.static import serve
import os

urlpatterns = [
    # FUERZA BRUTA: Servir assets directamente desde la raiz para evitar errores de cache/MIME
    re_path(r'^assets/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.FRONTEND_DIST_DIR, 'assets')
    }),
    re_path(r'^(?P<path>favicon\.ico|manifest\.json|vite\.svg|robots\.txt|sw\.js)$', serve, {
        'document_root': settings.FRONTEND_DIST_DIR
    }),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('apps.users.urls')),
    path('api/incidents/', include('apps.incidents.urls')),
    path('api/documents/', include('apps.documents.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/ai-orchestrator/', include('apps.ai_orchestrator.urls')),
    path('api/ai-agents/', include('apps.ai_agents.urls')),
    path('api/audit/', include('apps.audit.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
        path('api/notifications/', include('apps.notifications.urls')),
    path('api/integrations/', include('apps.integrations.urls')),
    path('api/sap/', include('apps.sap_integration.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Catch-all para el Frontend (React SPA)
from django.urls import re_path
from django.views.generic import TemplateView

urlpatterns += [
    # Comodín para cualquier ruta (maneja el routing de React)
    # Servimos index.html para que el navegador cargue la SPA
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]

if settings.DEBUG:
    # Solo en debug para archivos locales de media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
