#!/usr/bin/env python
"""
Script para probar la funcionalidad de imágenes
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.db import connection
from apps.incidents.models import Incident, IncidentImage
from apps.users.models import User

def test_image_functionality():
    """Probar la funcionalidad de imágenes"""
    print("Probando funcionalidad de imágenes...")
    
    try:
        # Verificar que la tabla incident_images existe
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'incident_images'
            """)
            
            if cursor.fetchone()[0] == 0:
                print("ERROR: La tabla incident_images no existe")
                return False
            
            print("✅ Tabla incident_images existe")
        
        # Verificar que hay incidencias
        incidents = Incident.objects.all()
        print(f"📊 Incidencias encontradas: {incidents.count()}")
        
        if incidents.count() == 0:
            print("⚠️ No hay incidencias para probar")
            return True
        
        # Verificar que hay imágenes
        images = IncidentImage.objects.all()
        print(f"🖼️ Imágenes encontradas: {images.count()}")
        
        # Mostrar detalles de las imágenes
        for image in images[:5]:  # Mostrar solo las primeras 5
            print(f"  - {image.filename} ({image.file_size} bytes) - {image.incident.code}")
        
        # Verificar relaciones
        for incident in incidents[:3]:  # Verificar las primeras 3 incidencias
            incident_images = incident.images.all()
            print(f"📋 {incident.code}: {incident_images.count()} imágenes")
            
            for img in incident_images:
                print(f"    - {img.filename} (subido por: {img.uploaded_by.username if img.uploaded_by else 'N/A'})")
        
        print("✅ Funcionalidad de imágenes verificada")
        return True
        
    except Exception as e:
        print(f"❌ Error al probar funcionalidad: {e}")
        return False

def main():
    """Función principal"""
    print("Iniciando prueba de funcionalidad de imágenes...")
    
    if test_image_functionality():
        print("Prueba completada exitosamente")
    else:
        print("Error en la prueba")
        sys.exit(1)

if __name__ == "__main__":
    main()
