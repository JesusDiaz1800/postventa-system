from django.urls import path
from . import views

urlpatterns = [
    # AI Analysis endpoints
    path('analyze-image/', views.analyze_image, name='analyze_image'),
    path('generate-text/', views.generate_text, name='generate_text'),
    
    # Provider management
    path('providers/status/', views.provider_status, name='provider_status'),
    path('providers/reset-quotas/', views.reset_quotas, name='reset_quotas'),
    
    # Analysis history
    path('analyses/', views.analysis_history, name='analysis_history'),
]
