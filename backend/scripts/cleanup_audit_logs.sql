-- Script SQL para limpiar logs de auditoría antiguos en SQL Server
-- Este script mantiene solo los logs con acciones permitidas

USE postventa_system;
GO

-- Ver cuántos logs se van a eliminar
SELECT 
    'Logs a eliminar' AS tipo,
    COUNT(*) AS cantidad
FROM audit_auditlog
WHERE action NOT IN (
    'user_login',
    'user_logout',
    'incident_created',
    'incident_closed',
    'escalation_triggered',
    'report_attached',
    'create',
    'delete',
    'item_restored'
);

-- Eliminar logs con acciones no permitidas
DELETE FROM audit_auditlog
WHERE action NOT IN (
    'user_login',
    'user_logout',
    'incident_created',
    'incident_closed',
    'escalation_triggered',
    'report_attached',
    'create',
    'delete',
    'item_restored'
);

-- Ver cuántos logs quedan
SELECT 
    'Logs restantes' AS tipo,
    COUNT(*) AS cantidad
FROM audit_auditlog;

-- Ver distribución de acciones restantes
SELECT 
    action,
    COUNT(*) AS cantidad
FROM audit_auditlog
GROUP BY action
ORDER BY cantidad DESC;
