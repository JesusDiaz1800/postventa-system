"""
Script para limpiar datos existentes y crear incidencias de ejemplo realistas
para demostracion del sistema de postventa Polifusion
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from datetime import timedelta, date, time
from apps.incidents.models import Incident, Category, Responsible, IncidentImage, IncidentTimeline
from apps.documents.models import VisitReport, LabReport, SupplierReport, QualityReport
from apps.users.models import User

def limpiar_datos():
    """Eliminar todos los datos existentes"""
    print("[LIMPIANDO] Datos existentes...")
    
    # Eliminar en orden para respetar FK
    IncidentTimeline.objects.all().delete()
    IncidentImage.objects.all().delete()
    VisitReport.objects.all().delete()
    LabReport.objects.all().delete()
    SupplierReport.objects.all().delete()
    QualityReport.objects.all().delete()
    Incident.objects.all().delete()
    
    print("[OK] Datos eliminados correctamente")

def crear_categorias():
    """Crear categorias si no existen"""
    categorias = [
        ('Tuberias PE', 'Tuberias de polietileno de alta densidad'),
        ('Fitting Electrofusion', 'Accesorios de electrofusion'),
        ('Fitting Mecanico', 'Accesorios de union mecanica'),
        ('Valvulas', 'Valvulas y accesorios de control'),
        ('Herramientas', 'Herramientas de instalacion y fusion'),
    ]
    
    for nombre, desc in categorias:
        Category.objects.get_or_create(name=nombre, defaults={'description': desc})
    
    print("[OK] Categorias creadas")
    return Category.objects.all()

def crear_responsables():
    """Crear responsables tecnicos si no existen"""
    responsables = [
        ('Carlos Mendoza', 'cmendoza@polifusion.cl'),
        ('Andrea Soto', 'asoto@polifusion.cl'),
        ('Roberto Figueroa', 'rfigueroa@polifusion.cl'),
    ]
    
    for nombre, email in responsables:
        Responsible.objects.get_or_create(name=nombre, defaults={'email': email, 'active': True})
    
    print("[OK] Responsables creados")
    return Responsible.objects.filter(active=True)

def crear_incidencias_demo():
    """Crear 5 incidencias realistas para demostracion"""
    
    categorias = list(crear_categorias())
    responsables = list(crear_responsables())
    
    # Obtener usuario admin o el primero disponible
    try:
        usuario = User.objects.first()
    except:
        usuario = None
    
    incidencias_data = [
        {
            'provider': 'Aliaxis Chile',
            'obra': 'Edificio Costanera Norte - Etapa 2',
            'cliente': 'Constructora Echeverria Izquierdo',
            'cliente_rut': '76.046.346-3',
            'direccion_cliente': 'Av. Presidente Kennedy 5413, Las Condes, Santiago',
            'sku': 'PE100-SDR11-110',
            'lote': 'L2024-1156',
            'factura_num': 'F-2024-004521',
            'pedido_num': 'PED-2024-0892',
            'fecha_deteccion': date.today() - timedelta(days=3),
            'hora_deteccion': time(9, 30),
            'descripcion': 'Se detecto fisura longitudinal en tuberia PE100 SDR11 de 110mm durante prueba hidraulica a 12 bar. La fisura se extiende aproximadamente 15cm en direccion axial. El problema fue detectado por el instalador durante la prueba de presion previa a la entrega.',
            'acciones_inmediatas': 'Se detuvo la prueba de presion inmediatamente. Se aislo el tramo afectado y se notifico al supervisor de obra. Se tomaron fotografias del defecto para documentacion.',
            'prioridad': 'alta',
            'estado': 'abierto',
            'subcategoria': 'Tuberia 110mm',
        },
        {
            'provider': 'Georg Fischer',
            'obra': 'Planta de Tratamiento Aguas Maipu',
            'cliente': 'Aguas Andinas S.A.',
            'cliente_rut': '61.808.000-5',
            'direccion_cliente': 'Camino Melipilla Km 12, Maipu, Santiago',
            'sku': 'EF-CODO-90-63',
            'lote': 'GF-2024-0783',
            'factura_num': 'F-2024-003892',
            'pedido_num': 'PED-2024-0756',
            'fecha_deteccion': date.today() - timedelta(days=7),
            'hora_deteccion': time(14, 15),
            'descripcion': 'Falla en electrofusion de codo 90 de 63mm. Despues de realizar el proceso de fusion segun parametros indicados, se observo que los indicadores de fusion no emergieron completamente. Al realizar prueba de presion, se detecto fuga en la union.',
            'acciones_inmediatas': 'Se realizo corte del fitting defectuoso y se instalo uno nuevo. El fitting retirado se guardo para analisis de laboratorio.',
            'prioridad': 'media',
            'estado': 'reporte_visita',
            'subcategoria': 'Codo EF 63mm',
            'escalated_to_quality': True,
            'escalation_date': timezone.now() - timedelta(days=5),
            'escalation_reason': 'Requiere analisis de laboratorio para determinar si es defecto de fabricacion',
        },
        {
            'provider': 'Plasson',
            'obra': 'Condominio Los Arrayanes',
            'cliente': 'Inmobiliaria Norte Verde',
            'cliente_rut': '77.123.456-7',
            'direccion_cliente': 'Av. Las Flores 2500, Chicureo, Colina',
            'sku': 'MECANICO-TEE-32',
            'lote': 'PL-2024-0445',
            'factura_num': 'F-2024-005123',
            'pedido_num': 'PED-2024-1023',
            'fecha_deteccion': date.today() - timedelta(days=1),
            'hora_deteccion': time(11, 45),
            'descripcion': 'Fitting mecanico tipo TEE de 32mm presenta rosca danada de fabrica. No permite el correcto apriete del inserto y genera fuga. Se detectaron 3 unidades con el mismo problema del mismo lote.',
            'acciones_inmediatas': 'Se separaron las 3 unidades defectuosas. Se utilizaron fittings de otro lote para continuar la instalacion.',
            'prioridad': 'baja',
            'estado': 'abierto',
            'subcategoria': 'TEE 32mm',
        },
        {
            'provider': 'Friatec',
            'obra': 'Red de Gas Natural - Sector Poniente',
            'cliente': 'Metrogas S.A.',
            'cliente_rut': '96.722.460-K',
            'direccion_cliente': 'El Salto 4001, Huechuraba, Santiago',
            'sku': 'VALV-BOLA-PE-63',
            'lote': 'FR-2024-2201',
            'factura_num': 'F-2024-004890',
            'pedido_num': 'PED-2024-0934',
            'fecha_deteccion': date.today() - timedelta(days=14),
            'hora_deteccion': time(8, 0),
            'descripcion': 'Valvula de bola PE de 63mm no cierra completamente. El actuador gira 90 grados pero la valvula permite paso de fluido. Problema critico para red de gas natural.',
            'acciones_inmediatas': 'Se reemplazo inmediatamente la valvula por una de stock. Se programo visita tecnica urgente del proveedor.',
            'prioridad': 'critica',
            'estado': 'proveedor',
            'subcategoria': 'Valvula Bola',
            'escalated_to_quality': True,
            'escalated_to_supplier': True,
            'escalation_date': timezone.now() - timedelta(days=12),
            'escalation_reason': 'Defecto critico en componente de seguridad para red de gas. Requiere analisis del fabricante.',
        },
        {
            'provider': 'Wavin',
            'obra': 'Hospital Regional de Talca',
            'cliente': 'Ministerio de Salud',
            'cliente_rut': '61.601.000-K',
            'direccion_cliente': '1 Norte 1990, Talca, Region del Maule',
            'sku': 'PE100-SDR17-200',
            'lote': 'WV-2024-0892',
            'factura_num': 'F-2024-003567',
            'pedido_num': 'PED-2024-0678',
            'fecha_deteccion': date.today() - timedelta(days=21),
            'hora_deteccion': time(16, 30),
            'descripcion': 'Deformacion ovalada en tuberia PE100 SDR17 de 200mm. La tuberia llego con deformacion permanente que impide la correcta insercion en fittings de electrofusion. Afecta 20 metros lineales.',
            'acciones_inmediatas': 'Se rechazo el material en bodega. Se solicito reposicion urgente al proveedor. Se documento fotograficamente la deformacion.',
            'prioridad': 'alta',
            'estado': 'cerrado',
            'subcategoria': 'Tuberia 200mm',
            'escalated_to_supplier': True,
            'escalation_date': timezone.now() - timedelta(days=18),
            'escalation_reason': 'Material defectuoso de origen. Requiere reposicion del proveedor.',
        },
    ]
    
    print("\n[CREANDO] Incidencias de demostracion...")
    
    for i, data in enumerate(incidencias_data):
        # Asignar categoria y responsable
        categoria = categorias[i % len(categorias)]
        responsable = responsables[i % len(responsables)]
        
        # Extraer campos especiales
        escalated_to_quality = data.pop('escalated_to_quality', False)
        escalated_to_supplier = data.pop('escalated_to_supplier', False)
        escalation_date = data.pop('escalation_date', None)
        escalation_reason = data.pop('escalation_reason', '')
        
        # Crear incidencia
        incidencia = Incident.objects.create(
            categoria=categoria,
            responsable=responsable,
            created_by=usuario,
            escalated_to_quality=escalated_to_quality,
            escalated_to_supplier=escalated_to_supplier,
            escalation_date=escalation_date,
            escalation_reason=escalation_reason,
            **data
        )
        
        print(f"   [OK] {incidencia.code} - {data['cliente'][:30]}...")
        
        # Agregar entrada en timeline
        IncidentTimeline.objects.create(
            incident=incidencia,
            action='created',
            user=usuario,
            description=f'Incidencia creada: {data["descripcion"][:100]}...'
        )
    
    print(f"\n[COMPLETADO] Se crearon {Incident.objects.count()} incidencias exitosamente!")

if __name__ == '__main__':
    print("=" * 60)
    print("   SCRIPT DE DATOS DE DEMOSTRACION - POSTVENTA POLIFUSION")
    print("=" * 60)
    
    limpiar_datos()
    crear_incidencias_demo()
    
    print("\n" + "=" * 60)
    print("   PROCESO COMPLETADO!")
    print("=" * 60)
