-- Script para identificar y limpiar adjuntos duplicados de la incidencia 20147
-- Paso 1: Ver todos los adjuntos actuales
SELECT 
    da.id,
    da.filename,
    da.document_type,
    da.document_id,
    da.uploaded_at,
    da.file
FROM documents_documentattachment da
WHERE da.document_type = 'supplier_response'
  AND da.document_id = 20147
ORDER BY da.uploaded_at;

-- Paso 2: Identificar duplicados (mismo archivo subido múltiples veces)
SELECT 
    da.filename,
    COUNT(*) as cantidad,
    GROUP_CONCAT(da.id) as ids,
    MIN(da.id) as id_mantener
FROM documents_documentattachment da
WHERE da.document_type = 'supplier_response'
  AND da.document_id = 20147
GROUP BY da.filename
HAVING COUNT(*) > 1;

-- Paso 3: ELIMINAR duplicados (mantener solo el más antiguo de cada archivo)
-- EJECUTAR CON CUIDADO - Esto borrará los adjuntos duplicados
DELETE FROM documents_documentattachment
WHERE id IN (
    SELECT id FROM (
        SELECT da2.id
        FROM documents_documentattachment da2
        INNER JOIN (
            SELECT filename, MIN(id) as id_mantener
            FROM documents_documentattachment
            WHERE document_type = 'supplier_response'
              AND document_id = 20147
            GROUP BY filename
        ) mantener ON da2.filename = mantener.filename
        WHERE da2.document_type = 'supplier_response'
          AND da2.document_id = 20147
          AND da2.id != mantener.id_mantener
    ) AS duplicados
);
