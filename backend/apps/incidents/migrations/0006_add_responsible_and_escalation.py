# Generated manually for responsible and escalation fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0005_update_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='responsable',
            field=models.CharField(
                choices=[
                    ('patricio_morales', 'Patricio Morales'),
                    ('marco_montenegro', 'Marco Montenegro'),
                ],
                help_text='Responsable técnico asignado',
                max_length=50,
                default='patricio_morales'
            ),
        ),
        migrations.AddField(
            model_name='incident',
            name='escalated_to_quality',
            field=models.BooleanField(
                default=False,
                help_text='Indica si la incidencia fue escalada a calidad'
            ),
        ),
        migrations.AddField(
            model_name='incident',
            name='escalated_to_supplier',
            field=models.BooleanField(
                default=False,
                help_text='Indica si la incidencia fue escalada a proveedor'
            ),
        ),
        migrations.AddField(
            model_name='incident',
            name='escalation_date',
            field=models.DateTimeField(
                blank=True,
                help_text='Fecha de escalamiento',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='incident',
            name='escalation_reason',
            field=models.TextField(
                blank=True,
                help_text='Razón del escalamiento'
            ),
        ),
    ]
