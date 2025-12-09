from django.urls import path
from .views_simple import audit_logs_list_simple, audit_dashboard_simple

urlpatterns = [
    path('logs/', audit_logs_list_simple, name='audit-logs-list'),
    path('dashboard/', audit_dashboard_simple, name='audit-dashboard'),
]
