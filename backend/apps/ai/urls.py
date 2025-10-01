"""
URLs para análisis con IA
"""
from django.urls import path
from . import views

urlpatterns = [
    path('analyze-image/', views.analyze_image, name='analyze_image'),
    path('analyze-failure-image/', views.analyze_failure_image, name='analyze_failure_image'),
    path('professionalize-description/', views.professionalize_problem_description, name='professionalize_problem_description'),
    path('service-status/', views.get_ai_service_status, name='get_ai_service_status'),
]