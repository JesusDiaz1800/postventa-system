"""
URLs para el sistema de auditoría
"""
from django.urls import path
from . import views, views_simple, views_fixed

urlpatterns = [
    # Lista y creación de logs
    path('logs/', views.AuditLogListCreateView.as_view(), name='audit_log_list_create'),
    path('logs/<int:pk>/', views.AuditLogRetrieveView.as_view(), name='audit_log_retrieve'),
    
    # Endpoints específicos
    path('logs/list/', views_fixed.audit_logs_list_fixed, name='audit_logs_list'),
    path('logs/simple/', views_fixed.audit_logs_simple, name='audit_logs_list_simple'),
    path('logs/export/', views.audit_logs_export, name='audit_logs_export'),
    path('logs/statistics/', views.audit_logs_statistics, name='audit_logs_statistics'),
]