from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.ReportTemplateViewSet)
router.register(r'instances', views.ReportInstanceViewSet)
router.register(r'schedules', views.ReportScheduleViewSet)
router.register(r'dashboards', views.ReportDashboardViewSet)
router.register(r'widgets', views.ReportWidgetViewSet)
router.register(r'exports', views.ReportExportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
