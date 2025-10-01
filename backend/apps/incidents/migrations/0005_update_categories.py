# Generated manually for category updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0004_create_incident_attachments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='categoria',
            field=models.CharField(
                choices=[
                    ('tuberia_beta', 'Tubería BETA'),
                    ('tuberia_ppr', 'Tubería PPR'),
                    ('tuberia_hdpe', 'Tubería HDPE'),
                    ('fitting_inserto_metalico', 'Fitting con inserto metálico'),
                    ('fitting_ppr', 'Fitting PPR'),
                    ('fitting_hdpe_electrofusion', 'Fitting HDPE Electrofusión'),
                    ('fitting_hdpe_fusion_tope', 'Fitting HDPE Fusión Tope'),
                    ('llave', 'LLave'),
                    ('flange', 'Flange'),
                    ('inserto_metalico', 'Inserto metálico'),
                    ('otro', 'Otro'),
                ],
                help_text='Categoría del producto',
                max_length=50
            ),
        ),
    ]
