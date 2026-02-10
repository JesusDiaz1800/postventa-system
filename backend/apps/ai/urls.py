"""
URLs para análisis con IA
"""
from django.urls import path
from . import views
from . import views_writing
from . import rag_views

urlpatterns = [
    path('analyze-image/', views.analyze_image, name='analyze_image'),
    path('analyze-failure-image/', views.analyze_failure_image, name='analyze_failure_image'),
    path('professionalize-description/', views.professionalize_problem_description, name='professionalize_problem_description'),
    path('service-status/', views.get_ai_service_status, name='get_ai_service_status'),
    path('status/', views.get_ai_service_status, name='get_ai_status_alias'),
    
    # Writing Assistant endpoints
    path('writing/improve/', views_writing.improve_text, name='ai_improve_text'),
    path('writing/fix/', views_writing.fix_errors, name='ai_fix_errors'),
    path('writing/generate-report/', views_writing.generate_report, name='ai_generate_report'),
    path('writing/suggest-terms/', views_writing.suggest_terms, name='ai_suggest_terms'),
    path('writing/expand-term/', views_writing.expand_term, name='ai_expand_term'),
    path('writing/analyze-closure/', views_writing.analyze_closure, name='ai_analyze_closure'),
    path('generate-text/', views_writing.generate_text, name='ai_generate_text'),
    
    # RAG Search
    path('rag/search/', rag_views.search_incidents, name='rag_search_incidents'),
]