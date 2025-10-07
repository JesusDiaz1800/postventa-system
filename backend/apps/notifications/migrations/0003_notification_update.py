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
        migrations.CreateModel(
            name='NotificationCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, max_length=50)),
                ('color', models.CharField(blank=True, max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Categoría de notificación',
                'verbose_name_plural': 'Categorías de notificaciones',
                'db_table': 'notification_categories',
            },
        ),
        migrations.AddField(
            model_name='notification',
            name='is_system',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notification',
            name='related_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('incident_created', 'Incidencia Creada'), ('incident_updated', 'Incidencia Actualizada'), ('incident_escalated', 'Incidencia Escalada'), ('incident_closed', 'Incidencia Cerrada'), ('document_uploaded', 'Documento Subido'), ('document_approved', 'Documento Aprobado'), ('document_rejected', 'Documento Rechazado'), ('workflow_step_completed', 'Paso de Workflow Completado'), ('workflow_approval_required', 'Aprobación de Workflow Requerida'), ('system_alert', 'Alerta del Sistema'), ('user_assigned', 'Usuario Asignado'), ('deadline_approaching', 'Fecha Límite Próxima'), ('deadline_exceeded', 'Fecha Límite Excedida'), ('quality_report_submitted', 'Reporte de Calidad Enviado'), ('quality_report_approved', 'Reporte de Calidad Aprobado'), ('quality_report_rejected', 'Reporte de Calidad Rechazado'), ('visit_report_submitted', 'Reporte de Visita Enviado'), ('visit_report_approved', 'Reporte de Visita Aprobado'), ('visit_report_rejected', 'Reporte de Visita Rechazado')], max_length=50),
        ),
        migrations.AlterField(
            model_name='notification',
            name='related_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_notifications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='NotificationPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_notifications', models.BooleanField(default=True)),
                ('push_notifications', models.BooleanField(default=True)),
                ('sound_enabled', models.BooleanField(default=True)),
                ('desktop_notifications', models.BooleanField(default=True)),
                ('notification_frequency', models.CharField(choices=[('real_time', 'Tiempo real'), ('daily', 'Diario'), ('weekly', 'Semanal')], default='real_time', max_length=20)),
                ('quiet_hours_start', models.TimeField(blank=True, null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categories', models.ManyToManyField(blank=True, related_name='user_preferences', to='notifications.notificationcategory')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Preferencias de notificaciones',
                'verbose_name_plural': 'Preferencias de notificaciones',
                'db_table': 'notification_preferences',
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['notification_type'], name='notification_notifica_2a4584_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_important'], name='notification_user_id_d4c27a_idx'),
        ),
        migrations.AddField(
            model_name='notification',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='notifications.notificationcategory'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['category'], name='notification_categor_1b5f3a_idx'),
        ),
    ]