-- Initialize database with basic data

-- Create admin user (password: admin123)
INSERT INTO users_user (username, email, password, role, is_active, is_staff, is_superuser, first_name, last_name, created_at, updated_at)
VALUES ('admin', 'admin@postventa.local', 'pbkdf2_sha256$600000$dummy$dummy', 'admin', true, true, true, 'Administrador', 'Sistema', NOW(), NOW())
ON CONFLICT (username) DO NOTHING;

-- Create default AI providers
INSERT INTO ai_orchestrator_aiprovider (name, enabled, priority, daily_quota_tokens, daily_quota_calls, quota_reset_time, tokens_used_today, calls_made_today, last_reset_date, allow_external_uploads, created_at, updated_at)
VALUES 
    ('openai', false, 1, 100000, 1000, '00:00', 0, 0, CURRENT_DATE, true, NOW(), NOW()),
    ('anthropic', false, 2, 100000, 1000, '00:00', 0, 0, CURRENT_DATE, true, NOW(), NOW()),
    ('google', false, 3, 100000, 1000, '00:00', 0, 0, CURRENT_DATE, true, NOW(), NOW()),
    ('local', true, 4, 0, 0, '00:00', 0, 0, CURRENT_DATE, false, NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Create default document templates
INSERT INTO documents_documenttemplate (name, template_type, description, docx_template_path, placeholders_json, is_active, created_by_id, created_at, updated_at)
VALUES 
    ('Informe Cliente', 'cliente_informe', 'Plantilla para informes dirigidos al cliente', 'templates/cliente_informe.docx', '["CLIENTE", "FECHA_DETECCION", "SKU", "LOTE", "DESCRIPCION", "CONCLUSIONES_TECNICAS", "RECOMENDACIONES", "FIRMANTE"]', true, 1, NOW(), NOW()),
    ('Carta Proveedor', 'proveedor_carta', 'Plantilla para cartas dirigidas al proveedor', 'templates/proveedor_carta.docx', '["PROVEEDOR", "LOTE", "NUM_PEDIDO", "DESCRIPCION", "CONCLUSIONES_TECNICAS", "FIRMANTE"]', true, 1, NOW(), NOW()),
    ('Reporte Laboratorio', 'lab_report', 'Plantilla para reportes de laboratorio', 'templates/lab_report.docx', '["INCIDENTE", "MUESTRA", "ENSAYOS", "OBSERVACIONES", "CONCLUSIONES", "EXPERTO"]', true, 1, NOW(), NOW())
ON CONFLICT DO NOTHING;
