"""
URL Configuration for AI Agents App
"""

from django.urls import path
from . import views

app_name = 'ai_agents'

urlpatterns = [
    path('query/', views.agent_query, name='agent_query'),
    path('analyze-image/', views.agent_analyze_image, name='agent_analyze_image'),
    path('status/', views.agent_status, name='agent_status'),
]
