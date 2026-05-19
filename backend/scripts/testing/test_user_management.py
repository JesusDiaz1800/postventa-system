#!/usr/bin/env python
"""
Script para probar la funcionalidad de gestión de usuarios
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.users.models import User
from django.contrib.auth.hashers import make_password

def test_user_management():
    """Probar la funcionalidad de gestión de usuarios"""
    print("👥 PROBANDO GESTIÓN DE USUARIOS...")
    print("=" * 50)
    
    # Crear usuario de prueba
    print("📝 Creando usuario de prueba...")
    try:
        test_user = User.objects.create(
            username='test_user_management',
            email='test@polifusion.cl',
            first_name='Usuario',
            last_name='Prueba',
            role='analyst',
            phone='+56912345678',
            department='Tecnología',
            is_active=True
        )
        test_user.set_password('TestPassword123!')
        test_user.save()
        print(f"✅ Usuario creado: {test_user.username} (ID: {test_user.id})")
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return
    
    # Probar actualización de usuario
    print("\n✏️  Actualizando usuario...")
    try:
        test_user.first_name = 'Usuario Actualizado'
        test_user.phone = '+56987654321'
        test_user.department = 'Calidad'
        test_user.save()
        print(f"✅ Usuario actualizado: {test_user.first_name}")
    except Exception as e:
        print(f"❌ Error actualizando usuario: {e}")
    
    # Probar cambio de rol
    print("\n🔄 Cambiando rol de usuario...")
    try:
        test_user.role = 'supervisor'
        test_user.save()
        print(f"✅ Rol cambiado a: {test_user.get_role_display()}")
    except Exception as e:
        print(f"❌ Error cambiando rol: {e}")
    
    # Probar desactivación de usuario
    print("\n🚫 Desactivando usuario...")
    try:
        test_user.is_active = False
        test_user.save()
        print(f"✅ Usuario desactivado: {test_user.is_active}")
    except Exception as e:
        print(f"❌ Error desactivando usuario: {e}")
    
    # Probar reactivación de usuario
    print("\n✅ Reactivando usuario...")
    try:
        test_user.is_active = True
        test_user.save()
        print(f"✅ Usuario reactivado: {test_user.is_active}")
    except Exception as e:
        print(f"❌ Error reactivando usuario: {e}")
    
    # Probar métodos de permisos
    print("\n🔐 Probando métodos de permisos...")
    try:
        print(f"   - Es admin: {test_user.is_admin()}")
        print(f"   - Es supervisor: {test_user.is_supervisor()}")
        print(f"   - Puede gestionar incidencias: {test_user.can_manage_incidents()}")
        print(f"   - Puede ver reportes: {test_user.can_view_reports()}")
        print(f"   - Puede gestionar usuarios: {test_user.can_manage_users()}")
    except Exception as e:
        print(f"❌ Error probando permisos: {e}")
    
    # Probar estadísticas
    print("\n📊 Probando estadísticas...")
    try:
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        admin_count = User.objects.filter(role='admin', is_active=True).count()
        supervisor_count = User.objects.filter(role='supervisor', is_active=True).count()
        
        print(f"   - Total usuarios: {total_users}")
        print(f"   - Usuarios activos: {active_users}")
        print(f"   - Administradores: {admin_count}")
        print(f"   - Supervisores: {supervisor_count}")
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
    
    # Limpiar usuario de prueba
    print("\n🧹 Limpiando usuario de prueba...")
    try:
        test_user.delete()
        print("✅ Usuario de prueba eliminado")
    except Exception as e:
        print(f"❌ Error eliminando usuario de prueba: {e}")
    
    print("\n🎉 Pruebas de gestión de usuarios completadas!")

def test_user_roles():
    """Probar diferentes roles de usuario"""
    print("\n👔 PROBANDO ROLES DE USUARIO...")
    print("=" * 50)
    
    roles = ['admin', 'supervisor', 'analyst', 'customer_service', 'management', 'provider']
    
    for role in roles:
        try:
            user = User.objects.create(
                username=f'test_{role}',
                email=f'{role}@polifusion.cl',
                first_name=f'Usuario {role.title()}',
                last_name='Prueba',
                role=role,
                is_active=True
            )
            user.set_password('TestPassword123!')
            user.save()
            
            print(f"✅ Usuario {role} creado: {user.get_role_display()}")
            print(f"   - Permisos: admin={user.is_admin()}, supervisor={user.is_supervisor()}")
            print(f"   - Gestionar incidencias: {user.can_manage_incidents()}")
            print(f"   - Ver reportes: {user.can_view_reports()}")
            print(f"   - Gestionar usuarios: {user.can_manage_users()}")
            
            # Limpiar
            user.delete()
            print(f"   - Usuario {role} eliminado")
            
        except Exception as e:
            print(f"❌ Error con rol {role}: {e}")

if __name__ == '__main__':
    test_user_management()
    test_user_roles()
