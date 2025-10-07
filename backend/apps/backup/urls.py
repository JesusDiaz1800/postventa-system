from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BackupJobViewSet, BackupInstanceViewSet, RestoreJobViewSet,
    BackupScheduleViewSet, BackupStorageViewSet, BackupLogViewSet,
    BackupPolicyViewSet
)

router = DefaultRouter()
router.register(r'jobs', BackupJobViewSet)
router.register(r'instances', BackupInstanceViewSet)
router.register(r'restores', RestoreJobViewSet)
router.register(r'schedules', BackupScheduleViewSet)
router.register(r'storages', BackupStorageViewSet)
router.register(r'logs', BackupLogViewSet)
router.register(r'policies', BackupPolicyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
