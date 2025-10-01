-- Script de limpieza manual de base de datos
-- Ejecutar este script en SQL Server Management Studio o Azure Data Studio

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
DROP TABLE IF EXISTS document_versions;
DROP TABLE IF EXISTS document_conversions;
DROP TABLE IF EXISTS document_templates;
DROP TABLE IF EXISTS documents;

-- 3. Verificar que las tablas se eliminaron
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME IN ('document_templates', 'documents', 'document_versions', 'document_conversions');

-- 4. Mostrar tablas restantes
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE' 
AND TABLE_NAME LIKE '%document%'
ORDER BY TABLE_NAME;
