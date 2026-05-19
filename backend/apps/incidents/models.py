from django.db import models
# Removed - Sertec Deep Audit - Model is dead but kept as skeleton to avoid migration crashes if referenced.
class Incident(models.Model):
    class Meta:
        managed = False
        db_table = 'incidents'
