from django.urls import path
from .views_simple import audit_logs_list, audit_action_choices

urlpatterns = [
    path('logs/', audit_logs_list, name='audit-logs-list'),
    path('action-choices/', audit_action_choices, name='audit-action-choices'),]