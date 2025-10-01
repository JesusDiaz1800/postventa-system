# Script de PowerShell para limpiar la base de datos
# Ejecutar como administrador

Write-Host "🧹 Iniciando limpieza de base de datos..." -ForegroundColor Green

# Configuración de conexión
$server = "localhost"
$database = "postventa_system"
$connectionString = "Server=$server;Database=$database;Trusted_Connection=True;"

try {
    # Crear conexión
    $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
    $connection.Open()
    
    Write-Host "✅ Conectado a la base de datos" -ForegroundColor Green
    
    # Script SQL para limpiar
    $cleanupScript = @"
-- 1. Eliminar foreign keys primero
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

-- 2. Eliminar tablas no utilizadas
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
    
    # Verificar tablas restantes
    $checkScript = @"
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE' 
AND TABLE_NAME LIKE '%document%'
ORDER BY TABLE_NAME;
"@
    
    $checkCommand = New-Object System.Data.SqlClient.SqlCommand($checkScript, $connection)
    $reader = $checkCommand.ExecuteReader()
    
    Write-Host "📋 Tablas de documentos restantes:" -ForegroundColor Yellow
    while ($reader.Read()) {
        Write-Host "  - $($reader[0])" -ForegroundColor White
    }
    $reader.Close()
    
} catch {
    Write-Host "❌ Error durante la limpieza: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    if ($connection) {
        $connection.Close()
        Write-Host "🔌 Conexión cerrada" -ForegroundColor Blue
    }
}

Write-Host "🎉 Proceso de limpieza finalizado" -ForegroundColor Green
