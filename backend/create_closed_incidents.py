#!/usr/bin/env python
"""
Script para crear incidencias cerradas para probar la funcionalidad de reabrir
"""
import os
import sys
import django
from datetime import datetime, date, time, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postventa_system.settings-sqlserver')
django.setup()

from apps.incidents.models import Incident
from apps.users.models import User

def create_closed_incidents():
    """Crear incidencias cerradas para probar reabrir"""
    print("🔧 Creando incidencias cerradas...")
    
    try:
        # Obtener usuario admin
        user = User.objects.first()
        if not user:
            print("❌ No hay usuarios en el sistema")
            return False
        
        # Datos para incidencias cerradas
        closed_incidents_data = [
            {
                'code': 'INC-2025-0006',
                'provider': 'Tuberías del Sur S.A.',
                'obra': 'Residencial Los Pinos',
                'cliente': 'Inmobiliaria Los Pinos',
                'cliente_rut': '44.555.666-7',
                'direccion_cliente': 'Calle Los Pinos 890, La Reina, Santiago',
                'sku': 'TUB-PPR-20',
                'lote': 'L2025006',
                'factura_num': 'FAC-006-2025',
                'pedido_num': 'PED-006-2025',
                'fecha_reporte': datetime.now() - timedelta(days=10),
                'fecha_deteccion': date.today() - timedelta(days=10),
                'hora_deteccion': time(10, 15),
                'descripcion': 'Tubería PPR de 20mm con fisura longitudinal. La fisura se extendía por 15cm y comprometía la estanqueidad del sistema.',
                'acciones_inmediatas': 'Se aisló el tramo afectado y se instaló una tubería de reemplazo temporal.',
                'categoria': 'tuberia_ppr',
                'subcategoria': 'fisura',
                'prioridad': 'alta',
                'estado': 'cerrado',
                'responsable': 'patricio_morales',
                'acciones_posteriores': 'Se reemplazó completamente el tramo afectado y se realizó prueba de presión.',
                'fecha_cierre': date.today() - timedelta(days=5),
                'closed_by': user,
                'closed_at': datetime.now() - timedelta(days=5)
            },
            {
                'code': 'INC-2025-0007',
                'provider': 'Accesorios del Pacífico',
                'obra': 'Oficinas Corporativas Norte',
                'cliente': 'Corporación Norte S.A.',
                'cliente_rut': '55.666.777-8',
                'direccion_cliente': 'Av. Apoquindo 3000, Las Condes, Santiago',
                'sku': 'FITTING-HDPE-32',
                'lote': 'L2025007',
                'factura_num': 'FAC-007-2025',
                'pedido_num': 'PED-007-2025',
                'fecha_reporte': datetime.now() - timedelta(days=8),
                'fecha_deteccion': date.today() - timedelta(days=8),
                'hora_deteccion': time(14, 30),
                'descripcion': 'Fitting HDPE de 32mm con defecto en la soldadura. La unión presentaba porosidad que comprometía la estanqueidad.',
                'acciones_inmediatas': 'Se desmontó el fitting defectuoso y se instaló uno nuevo con soldadura correcta.',
                'categoria': 'fitting_hdpe_electrofusion',
                'subcategoria': 'defecto_soldadura',
                'prioridad': 'media',
                'estado': 'cerrado',
                'responsable': 'marco_montenegro',
                'acciones_posteriores': 'Se realizó inspección de todas las uniones similares para prevenir futuros problemas.',
                'fecha_cierre': date.today() - timedelta(days=3),
                'closed_by': user,
                'closed_at': datetime.now() - timedelta(days=3)
            }
        ]
        
        created_incidents = []
        
        for incident_data in closed_incidents_data:
            # Verificar si la incidencia ya existe
            if Incident.objects.filter(code=incident_data['code']).exists():
                print(f"⚠️ Incidencia {incident_data['code']} ya existe, saltando...")
                continue
            
            incident = Incident.objects.create(
                created_by=user,
                **incident_data
            )
            
            created_incidents.append(incident)
            print(f"✅ Incidencia cerrada creada: {incident.code} - {incident.cliente}")
        
        print(f"\n📊 Total de incidencias cerradas creadas: {len(created_incidents)}")
        return created_incidents
        
    except Exception as e:
        print(f"❌ Error creando incidencias cerradas: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("🚀 Creando incidencias cerradas para pruebas...")
    
    incidents = create_closed_incidents()
    
    if incidents:
        print("\n🎉 ¡Incidencias cerradas creadas exitosamente!")
        print("Ahora puedes probar:")
        print("- Ver incidencias cerradas en la tabla")
        print("- Usar el botón de reabrir (icono de flecha circular)")
        print("- Verificar que las incidencias cambien a estado 'abierto'")
    else:
        print("❌ No se pudieron crear las incidencias cerradas")
