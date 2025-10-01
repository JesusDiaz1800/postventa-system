# Generated manually to optimize incidents table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0008_make_sku_optional'),
    ]

    operations = [
        # Agregar índices para mejorar rendimiento
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_estado')
                CREATE INDEX idx_incidents_estado ON incidents(estado);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_estado;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_prioridad')
                CREATE INDEX idx_incidents_prioridad ON incidents(prioridad);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_prioridad;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_categoria')
                CREATE INDEX idx_incidents_categoria ON incidents(categoria);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_categoria;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_responsable')
                CREATE INDEX idx_incidents_responsable ON incidents(responsable);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_responsable;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_escalated_quality')
                CREATE INDEX idx_incidents_escalated_quality ON incidents(escalated_to_quality);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_escalated_quality;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_escalated_supplier')
                CREATE INDEX idx_incidents_escalated_supplier ON incidents(escalated_to_supplier);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_escalated_supplier;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_created_at')
                CREATE INDEX idx_incidents_created_at ON incidents(created_at);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_created_at;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_fecha_deteccion')
                CREATE INDEX idx_incidents_fecha_deteccion ON incidents(fecha_deteccion);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_fecha_deteccion;"
        ),
        # Índice compuesto para consultas frecuentes
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_estado_prioridad')
                CREATE INDEX idx_incidents_estado_prioridad ON incidents(estado, prioridad);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_estado_prioridad;"
        ),
        migrations.RunSQL(
            """
            IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_incidents_escalated_status')
                CREATE INDEX idx_incidents_escalated_status ON incidents(escalated_to_quality, escalated_to_supplier);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_incidents_escalated_status;"
        ),
    ]
