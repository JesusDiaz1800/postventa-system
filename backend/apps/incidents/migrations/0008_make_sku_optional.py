# Generated manually for making sku field optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0007_simplify_states_and_remove_lab_required'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='sku',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text='Código SKU del producto'
            ),
        ),
    ]
