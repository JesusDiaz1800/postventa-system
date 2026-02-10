
import os
import sys
import django
from django.db import transaction

# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')
django.setup()

from apps.incidents.models import Incident

def reorder_incidents():
    print("=== REORDENAMIENTO DE CÓDIGOS DE INCIDENCIA ===")
    print("Estrategia: INC-[AñoDetección]-[Correlativo]")
    
    try:
        with transaction.atomic():
            # Obtener todas las incidencias ordenadas por fecha de detección y creación
            # Usamos created_at como desempate para mantener el orden de ingreso relativo
            all_incidents = Incident.objects.all().order_by('fecha_deteccion', 'created_at')
            
            if not all_incidents.exists():
                print("No hay incidencias para procesar.")
                return

            print(f"Total de incidencias encontradas: {all_incidents.count()}")

            # Agrupar por año de detección
            from collections import defaultdict
            incidents_by_year = defaultdict(list)
            
            for incident in all_incidents:
                # Si por alguna razón no tiene fecha de detección, usar año actual como fallback
                if not incident.fecha_deteccion:
                    print(f"ADVERTENCIA: Incidencia {incident.id} sin fecha de detección. Usando año actual.")
                    year = django.utils.timezone.now().year
                else:
                    year = incident.fecha_deteccion.year
                
                incidents_by_year[year].append(incident)
                
            # FASE 1: Asignar códigos temporales
            # Esto es crucial para evitar errores de "Unique Constraint" si un código nuevo
            # colisiona con uno existente que aún no ha sido renombrado.
            print("\n>> FASE 1: Asignando códigos temporales...")
            for incident in all_incidents:
                temp_code = f"TEMP-{incident.id}-{incident.code}"
                # Cortar si es muy largo (aunque el campo da para 20 chars, max_length=20)
                # El modelo define max_length=20. TEMP-9999-INC... podría pasarse.
                # Usaremos un safe temp code corto.
                safe_temp_code = f"TMP-{incident.id}" 
                incident.code = safe_temp_code
                incident.save(update_fields=['code'])
            
            print("Códigos temporales asignados correctamente.")
                
            # FASE 2: Asignar códigos definitivos
            print("\n>> FASE 2: Asignando nuevos códigos secuenciales...")
            total_updated = 0
            
            for year in sorted(incidents_by_year.keys()):
                counter = 1
                year_group = incidents_by_year[year]
                print(f"\nProcesando Año {year} ({len(year_group)} incidencias):")
                
                for incident in year_group:
                    new_code = f'INC-{year}-{counter:04d}'
                    
                    # Log del cambio
                    # print(f"  {incident.fecha_deteccion} | ID {incident.id}: {incident.code} -> {new_code}")
                    
                    incident.code = new_code
                    incident.save(update_fields=['code'])
                    
                    counter += 1
                    total_updated += 1
                    
            print(f"\nProceso completado exitosamente. {total_updated} incidencias reordenadas.")
            
    except Exception as e:
        print(f"\nERROR CRÍTICO: {str(e)}")
        print("Se ha hecho rollback de todos los cambios.")
        sys.exit(1)

if __name__ == '__main__':
    reorder_incidents()
