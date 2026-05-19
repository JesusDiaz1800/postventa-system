from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPES = (
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('sap', 'Sincronización SAP'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPES, default='info')
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    related_url = models.CharField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

class NotificationPreferences(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    categories = models.JSONField(default=list) # ['general', 'sap', 'reports']
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferencias de {self.user.username}"
