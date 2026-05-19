"""
URL Configuration for AI Agents App
"""

from django.urls import path
from . import views

app_name = 'ai_agents'

urlpatterns = [
    path('query/', views.agent_query, name='agent_query'),
    path('analyze-image/', views.agent_analyze_image, name='agent_analyze_image'),
    path('generate-report/', views.agent_generate_report, name='agent_generate_report'),
    path('status/', views.agent_status, name='agent_status'),
]
