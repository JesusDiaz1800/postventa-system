from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'external-systems', views.ExternalSystemViewSet)
router.register(r'templates', views.IntegrationTemplateViewSet)
router.register(r'instances', views.IntegrationInstanceViewSet)
router.register(r'logs', views.IntegrationLogViewSet)
router.register(r'webhook-endpoints', views.WebhookEndpointViewSet)
router.register(r'webhook-logs', views.WebhookLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
