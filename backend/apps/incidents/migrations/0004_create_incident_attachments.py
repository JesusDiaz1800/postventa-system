# Generated manually to create incident_attachments table

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0003_auto_20250917_0823'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(help_text='Nombre del archivo', max_length=255)),
                ('file_path', models.CharField(help_text='Ruta del archivo en el sistema', max_length=500)),
                ('file_size', models.BigIntegerField(help_text='Tamaño del archivo en bytes')),
                ('file_type', models.CharField(choices=[('image', 'Imagen'), ('document', 'Documento'), ('video', 'Video'), ('audio', 'Audio'), ('other', 'Otro')], help_text='Tipo de archivo', max_length=20)),
                ('mime_type', models.CharField(help_text='Tipo MIME del archivo', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Descripción del adjunto', null=True)),
                ('uploaded_at', models.DateTimeField(default=timezone.now, help_text='Fecha y hora de subida')),
                ('is_public', models.BooleanField(default=True, help_text='Si el adjunto es público o privado')),
                ('incident', models.ForeignKey(help_text='Incidencia a la que pertenece el adjunto', on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='incidents.incident')),
                ('uploaded_by', models.ForeignKey(help_text='Usuario que subió el archivo', on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_attachments', to='users.user')),
            ],
            options={
                'verbose_name': 'Adjunto de Incidencia',
                'verbose_name_plural': 'Adjuntos de Incidencias',
                'db_table': 'incident_attachments',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
