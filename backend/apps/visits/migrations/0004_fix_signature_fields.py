from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('visits', '0003_visitreport_incident_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitreport',
            name='technician_signature',
            field=models.TextField(blank=True, null=True, verbose_name='Firma Técnico (Base64)'),
        ),
        migrations.AlterField(
            model_name='visitreport',
            name='installer_signature',
            field=models.TextField(blank=True, null=True, verbose_name='Firma Instalador (Base64)'),
        ),
    ]
