#!/usr/bin/env python
"""
Script simple para verificar la configuración de base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from django.conf import settings
from django.db import connection
from apps.incidents.models import Incident
from apps.users.models import User

def verify_database():
    """Verificar configuración de base de datos"""
    print("=" * 60)
    print("    VERIFICACION DE BASE DE DATOS")
    print("=" * 60)
    
    try:
        # 1. Verificar configuración
        print("\n1. CONFIGURACION DE DJANGO")
        print(f"   ENGINE: {settings.DATABASES['default']['ENGINE']}")
        print(f"   HOST: {settings.DATABASES['default']['HOST']}")
        print(f"   DATABASE: {settings.DATABASES['default']['NAME']}")
        
        # 2. Verificar conexión
        print("\n2. CONEXION A BASE DE DATOS")
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"   OK - Conectado a SQL Server")
            print(f"   Version: {version[:50]}...")
        
        # 3. Verificar incidencias
        print("\n3. INCIDENCIAS EN BASE DE DATOS")
        incidents = Incident.objects.all()
        print(f"   Total incidencias: {incidents.count()}")
        
        for incident in incidents:
            print(f"   - ID: {incident.id}")
            print(f"     Codigo: {incident.code}")
            print(f"     Cliente: {incident.cliente}")
            print(f"     Estado: {incident.estado}")
            print()
        
        # 4. Verificar usuarios
        print("4. USUARIOS EN BASE DE DATOS")
        users = User.objects.all()
        print(f"   Total usuarios: {users.count()}")
        
        # Buscar usuario jdiaz
        try:
            user = User.objects.get(username='jdiaz')
            print(f"   OK - Usuario 'jdiaz' encontrado (ID: {user.id})")
        except User.DoesNotExist:
            print("   ERROR - Usuario 'jdiaz' no encontrado")
        
        print("\n" + "=" * 60)
        print("    VERIFICACION COMPLETADA")
        print("=" * 60)
        
        if incidents.count() == 2:
            print("OK - SISTEMA CONFIGURADO CORRECTAMENTE")
            print("   - Base de datos: SQL Server Express")
            print("   - Incidencias: 2 encontradas")
            print("   - Usuario: jdiaz disponible")
        else:
            print("ADVERTENCIA - REVISAR CONFIGURACION")
            print(f"   - Incidencias esperadas: 2")
            print(f"   - Incidencias encontradas: {incidents.count()}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nPosibles causas:")
        print("1. SQL Server Express no esta ejecutandose")
        print("2. Driver ODBC no esta instalado")
        print("3. Permisos de acceso insuficientes")
        print("4. Instancia SQL Server no disponible")

if __name__ == "__main__":
    verify_database()
