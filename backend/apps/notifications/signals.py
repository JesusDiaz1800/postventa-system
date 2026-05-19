from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import NotificationPreferences

User = get_user_model()

@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """
    Crea automáticamente el perfil de preferencias de notificación 
    cuando se registra un nuevo usuario en Sertec.
    """
    if created:
        NotificationPreferences.objects.get_or_create(user=instance)
