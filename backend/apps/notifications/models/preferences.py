from django.db import models
from django.contrib.auth import get_user_model

# Make Postgres-specific ArrayField optional to avoid import-time errors when
# psycopg/psycopg2 is not installed (we fall back to JSONField on other DBs).
try:
    from django.contrib.postgres.fields import ArrayField  # type: ignore
    POSTGRES_ARRAY_AVAILABLE = True
except Exception:
    ArrayField = models.JSONField  # type: ignore
    POSTGRES_ARRAY_AVAILABLE = False

User = get_user_model()


class NotificationPreferences(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, usa TextField para listas y considera migrar a ManyToMany en el futuro.
    def get_categories(self):
        """Devuelve las categorías como lista (desde TextField serializado)."""
        if not self.categories:
            return []
        # Intentar parsear como JSON, si falla usar CSV
        import json
        try:
            return json.loads(self.categories)
        except Exception:
            return [c.strip() for c in self.categories.split(',') if c.strip()]
    """Modelo para almacenar las preferencias de notificaciones del usuario"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    # ADVERTENCIA: ArrayField solo es compatible con PostgreSQL. Para SQL Server, migrar a ManyToManyField o tabla relacionada en el futuro.
    categories = models.TextField(blank=True, default='')
    # ADVERTENCIA: Para compatibilidad con SQL Express y futura migración a SQL Server,
    # se utiliza TextField para almacenar categorías como lista serializada (ej: JSON o CSV).
    # En PostgreSQL se recomienda usar ArrayField, y en SQL Server migrar a ManyToManyField.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Preferencias de notificaciones'
        verbose_name_plural = 'Preferencias de notificaciones'

    def __str__(self):
        return f'Preferencias de {self.user.username}'