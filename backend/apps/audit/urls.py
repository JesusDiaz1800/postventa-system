<<<<<<< HEAD
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuditLogViewSet,
    AuditRuleViewSet,
    AuditReportViewSet,
    AuditDashboardViewSet,
    AuditAlertViewSet,
    AuditStatsViewSet,
    AuditSearchViewSet
)

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet, basename='audit-log')
router.register(r'rules', AuditRuleViewSet, basename='audit-rule')
router.register(r'reports', AuditReportViewSet, basename='audit-report')
router.register(r'dashboards', AuditDashboardViewSet, basename='audit-dashboard')
router.register(r'alerts', AuditAlertViewSet, basename='audit-alert')
router.register(r'stats', AuditStatsViewSet, basename='audit-stats')
router.register(r'search', AuditSearchViewSet, basename='audit-search')

urlpatterns = [
    path('api/', include(router.urls)),
=======
from django.urls import path
from .views_simple import audit_logs_list, audit_action_choices

urlpatterns = [
    path('logs/', audit_logs_list, name='audit-logs-list'),
    path('action-choices/', audit_action_choices, name='audit-action-choices'),
>>>>>>> 674c244 (tus cambios)
]