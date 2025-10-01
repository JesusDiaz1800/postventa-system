#!/usr/bin/env python
"""
Script para crear la tabla de auditoría manualmente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings')
django.setup()

def create_audit_table():
    """Crear la tabla de auditoría manualmente"""
    try:
        print("Creando tabla de auditoria manualmente...")
        
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Crear la tabla de auditoría
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action VARCHAR(20) NOT NULL,
                    resource_type VARCHAR(30) NOT NULL,
                    resource_id VARCHAR(100) NOT NULL,
                    content_type_id INTEGER,
                    object_id INTEGER,
                    details TEXT NOT NULL,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    metadata JSON,
                    created_at DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES auth_user (id),
                    FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
                );
            """)
            
            print("Tabla audit_logs creada exitosamente")
            
            # Crear algunos logs de auditoría de prueba
            print("Creando logs de auditoría de prueba...")
            
            from django.contrib.auth.models import User
            
            user = User.objects.first()
            if user:
                cursor.execute("""
                    INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, datetime('now'))
                """, [user.id, 'create', 'incident', '1', 'Incidente creado para prueba', '127.0.0.1', 'Test Agent'])
                
                cursor.execute("""
                    INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, datetime('now'))
                """, [user.id, 'update', 'incident', '1', 'Incidente actualizado', '127.0.0.1', 'Test Agent'])
                
                print("Logs de auditoría de prueba creados")
        
        print("Tabla de auditoría creada exitosamente")
        
    except Exception as e:
        print(f"Error creando tabla: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_audit_table()
