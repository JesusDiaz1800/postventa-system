from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MonitoringRuleViewSet, AlertViewSet, MetricValueViewSet,
    HealthCheckViewSet, HealthCheckResultViewSet, SystemMetricsViewSet,
    NotificationChannelViewSet, AlertTemplateViewSet, MonitoringDashboardViewSet,
    MonitoringWidgetViewSet, MonitoringStatisticsViewSet
)

router = DefaultRouter()
router.register(r'rules', MonitoringRuleViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'metrics', MetricValueViewSet)
router.register(r'health-checks', HealthCheckViewSet)
router.register(r'health-check-results', HealthCheckResultViewSet)
router.register(r'system-metrics', SystemMetricsViewSet)
router.register(r'notification-channels', NotificationChannelViewSet)
router.register(r'alert-templates', AlertTemplateViewSet)
router.register(r'dashboards', MonitoringDashboardViewSet)
router.register(r'widgets', MonitoringWidgetViewSet)
router.register(r'statistics', MonitoringStatisticsViewSet, basename='monitoring-statistics')

urlpatterns = [
    path('', include(router.urls)),
]
