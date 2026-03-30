from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0022_add_search_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='provider',
            field=models.CharField(blank=True, db_index=True, help_text='Proveedor del producto', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='incident',
            name='sku',
            field=models.CharField(db_index=True, default='N/A', help_text='SKU del producto', max_length=100),
        ),
        migrations.AlterField(
            model_name='incident',
            name='fecha_deteccion',
            field=models.DateField(db_index=True, help_text='Fecha de detección del problema'),
        ),
    ]
