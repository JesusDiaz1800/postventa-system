-- Script to add missing columns to integrations_webhookendpoint table
-- Run this in SQL Server Management Studio or via a DB client

-- Check if columns exist before adding
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'description')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD description NVARCHAR(MAX) NULL;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'url_path')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD url_path NVARCHAR(200) NOT NULL DEFAULT '';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'http_method')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD http_method NVARCHAR(10) NOT NULL DEFAULT 'POST';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'requires_auth')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD requires_auth BIT NOT NULL DEFAULT 1;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'auth_token')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD auth_token NVARCHAR(255) NULL;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'validate_signature')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD validate_signature BIT NOT NULL DEFAULT 0;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'signature_header')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD signature_header NVARCHAR(100) NULL;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'signature_secret')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD signature_secret NVARCHAR(255) NULL;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'auto_process')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD auto_process BIT NOT NULL DEFAULT 1;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'processing_script')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD processing_script NVARCHAR(MAX) NULL;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'integrations_webhookendpoint') AND name = 'filter_conditions')
BEGIN
    ALTER TABLE integrations_webhookendpoint ADD filter_conditions NVARCHAR(MAX) NULL;
END

PRINT 'Missing columns added successfully!';
