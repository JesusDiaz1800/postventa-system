# Script simple de limpieza de base de datos
Write-Host "🧹 Iniciando limpieza de base de datos..." -ForegroundColor Green

try {
    # Crear conexión
    $connectionString = "Server=localhost;Database=postventa_system;Trusted_Connection=True;"
    $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
    $connection.Open()
    
    Write-Host "✅ Conectado a la base de datos" -ForegroundColor Green
    
    # Script de limpieza
    $cleanupScript = @"
-- Eliminar foreign keys primero
IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'document_versions_created_by_id_fk')
    ALTER TABLE document_versions DROP CONSTRAINT document_versions_created_by_id_fk;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'document_conversions_created_by_id_fk')
    ALTER TABLE document_conversions DROP CONSTRAINT document_conversions_created_by_id_fk;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'document_templates_created_by_id_fk')
    ALTER TABLE document_templates DROP CONSTRAINT document_templates_created_by_id_fk;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'documents_created_by_id_fk')
    ALTER TABLE documents DROP CONSTRAINT documents_created_by_id_fk;

IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'documents_incident_id_fk')
    ALTER TABLE documents DROP CONSTRAINT documents_incident_id_fk;

-- Eliminar tablas
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'document_versions')
    DROP TABLE document_versions;

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'document_conversions')
    DROP TABLE document_conversions;

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'document_templates')
    DROP TABLE document_templates;

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'documents')
    DROP TABLE documents;

PRINT 'Limpieza completada exitosamente';
"@
    
    # Ejecutar script
    $command = New-Object System.Data.SqlClient.SqlCommand($cleanupScript, $connection)
    $command.ExecuteNonQuery()
    
    Write-Host "✅ Limpieza completada exitosamente" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    if ($connection) {
        $connection.Close()
    }
}

Write-Host "🎉 Proceso finalizado" -ForegroundColor Green
