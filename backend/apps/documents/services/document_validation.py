#!/usr/bin/env python
"""
Servicio de validación de documentos para evitar duplicados
"""

from django.db.models import Q
from apps.documents.models import VisitReport, SupplierReport, LabReport, QualityReport
from apps.incidents.models import Incident
import logging

logger = logging.getLogger(__name__)

class DocumentValidationService:
    """
    Servicio para validar que no se generen documentos duplicados
    """
    
    @staticmethod
    def can_create_visit_report(incident_id):
        """
        Verificar si se puede crear un reporte de visita para una incidencia
        """
        try:
            # Verificar que la incidencia existe
            incident = Incident.objects.get(id=incident_id)
            
            # Verificar que no existe ya un reporte de visita para esta incidencia
            existing_report = VisitReport.objects.filter(related_incident=incident).first()
            
            if existing_report:
                return False, f"Ya existe un reporte de visita para la incidencia {incident.code}"
            
            return True, "Se puede crear el reporte de visita"
            
        except Incident.DoesNotExist:
            return False, "La incidencia no existe"
        except Exception as e:
            logger.error(f"Error validando reporte de visita: {str(e)}")
            return False, f"Error de validación: {str(e)}"
    
    @staticmethod
    def can_create_supplier_report(incident_id):
        """
        Verificar si se puede crear un reporte de proveedor para una incidencia
        """
        try:
            # Verificar que la incidencia existe
            incident = Incident.objects.get(id=incident_id)
            
            # Verificar que no existe ya un reporte de proveedor para esta incidencia
            existing_report = SupplierReport.objects.filter(related_incident=incident).first()
            
            if existing_report:
                return False, f"Ya existe un reporte de proveedor para la incidencia {incident.code}"
            
            return True, "Se puede crear el reporte de proveedor"
            
        except Incident.DoesNotExist:
            return False, "La incidencia no existe"
        except Exception as e:
            logger.error(f"Error validando reporte de proveedor: {str(e)}")
            return False, f"Error de validación: {str(e)}"
    
    @staticmethod
    def can_create_lab_report(incident_id):
        """
        Verificar si se puede crear un reporte de laboratorio para una incidencia
        """
        try:
            # Verificar que la incidencia existe
            incident = Incident.objects.get(id=incident_id)
            
            # Verificar que no existe ya un reporte de laboratorio para esta incidencia
            existing_report = LabReport.objects.filter(related_incident=incident).first()
            
            if existing_report:
                return False, f"Ya existe un reporte de laboratorio para la incidencia {incident.code}"
            
            return True, "Se puede crear el reporte de laboratorio"
            
        except Incident.DoesNotExist:
            return False, "La incidencia no existe"
        except Exception as e:
            logger.error(f"Error validando reporte de laboratorio: {str(e)}")
            return False, f"Error de validación: {str(e)}"
    
    @staticmethod
    def can_create_quality_report(incident_id, report_type='cliente'):
        """
        Verificar si se puede crear un reporte de calidad para una incidencia
        """
        try:
            # Verificar que la incidencia existe
            incident = Incident.objects.get(id=incident_id)
            
            # Verificar que no existe ya un reporte de calidad del mismo tipo para esta incidencia
            existing_report = QualityReport.objects.filter(
                related_incident=incident,
                report_type=report_type
            ).first()
            
            if existing_report:
                return False, f"Ya existe un reporte de calidad ({report_type}) para la incidencia {incident.code}"
            
            return True, f"Se puede crear el reporte de calidad ({report_type})"
            
        except Incident.DoesNotExist:
            return False, "La incidencia no existe"
        except Exception as e:
            logger.error(f"Error validando reporte de calidad: {str(e)}")
            return False, f"Error de validación: {str(e)}"
    
    @staticmethod
    def get_incident_documents_status(incident_id):
        """
        Obtener el estado de todos los documentos de una incidencia
        """
        try:
            incident = Incident.objects.get(id=incident_id)
            
            status = {
                'incident_code': incident.code,
                'incident_status': incident.estado,
                'visit_report': False,
                'supplier_report': False,
                'lab_report': False,
                'quality_report_cliente': False,
                'quality_report_interno': False
            }
            
            # Verificar reporte de visita
            if VisitReport.objects.filter(related_incident=incident).exists():
                status['visit_report'] = True
            
            # Verificar reporte de proveedor
            if SupplierReport.objects.filter(related_incident=incident).exists():
                status['supplier_report'] = True
            
            # Verificar reporte de laboratorio
            if LabReport.objects.filter(related_incident=incident).exists():
                status['lab_report'] = True
            
            # Verificar reportes de calidad
            if QualityReport.objects.filter(related_incident=incident, report_type='cliente').exists():
                status['quality_report_cliente'] = True
            
            if QualityReport.objects.filter(related_incident=incident, report_type='interno').exists():
                status['quality_report_interno'] = True
            
            return status
            
        except Incident.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error obteniendo estado de documentos: {str(e)}")
            return None
