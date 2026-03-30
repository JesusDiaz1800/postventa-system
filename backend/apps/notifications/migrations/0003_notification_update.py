from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0002_add_notification_preferences'),
    ]

    operations = [
        # This migration was redundant and caused conflicts. 
        # Making it a NO-OP to preserve dependency chain.
    ]