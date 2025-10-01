# Generated manually for simplifying states and removing lab_required

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0006_add_responsible_and_escalation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incident',
            name='lab_required',
        ),
        migrations.AlterField(
            model_name='incident',
            name='estado',
            field=models.CharField(
                choices=[
                    ('abierto', 'Abierto'),
                    ('cerrado', 'Cerrado'),
                ],
                default='abierto',
                help_text='Estado actual de la incidencia',
                max_length=20
            ),
        ),
    ]
