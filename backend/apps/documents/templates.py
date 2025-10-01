"""
Plantillas de documentos con placeholders específicos extraídos de los PDFs
"""
from typing import Dict, Any, Optional
from django.conf import settings
from apps.incidents.models import Incident
from apps.users.models import User


class DocumentTemplate:
    """Clase base para plantillas de documentos"""
    
    def __init__(self, template_name: str, template_type: str):
        self.template_name = template_name
        self.template_type = template_type
        self.placeholders = self._get_placeholders()
    
    def _get_placeholders(self) -> Dict[str, str]:
        """Obtener placeholders específicos de los PDFs"""
        return {
            'INC_CODE': 'Código de incidencia',
            'FECHA_DETECCION': 'Fecha de detección',
            'HORA_DETECCION': 'Hora de detección',
            'PROVEEDOR': 'Proveedor',
            'OBRA': 'Obra/Proyecto',
            'CLIENTE': 'Cliente',
            'CLIENTE_RUT': 'RUT del cliente',
            'DIRECCION': 'Dirección del cliente',
            'NUM_PEDIDO': 'Número de pedido',
            'NUM_FACTURA': 'Número de factura',
            'NC_NUMBER': 'Número de NC',
            'NP_NUMBER': 'Número de NP',
            'SKU': 'SKU del producto',
            'LOTE': 'Lote/Batch',
            'DESCRIPCION': 'Descripción del problema',
            'ACCIONES_INMEDIATAS': 'Acciones inmediatas adoptadas',
            'ACCIONES_POSTERIORES': 'Registro de evolución/acciones posteriores',
            'ANALISIS_IA': 'Análisis de IA',
            'CONCLUSIONES_TECNICAS': 'Conclusiones técnicas',
            'RECOMENDACIONES': 'Recomendaciones',
            'FIRMANTE': 'Nombre del firmante',
            'FIRMA_CARGO': 'Cargo del firmante',
            'ANEXOS_FOTOS': 'Lista de fotos anexas',
            'FECHA_FIRMA': 'Fecha de firma',
            'EXPERTO': 'Nombre del experto',
            'ENSAYOS': 'Ensayos realizados',
            'OBSERVACIONES': 'Observaciones',
            'RESULTADOS': 'Resultados',
            'CONCLUSIONES': 'Conclusiones',
        }
    
    def get_context(self, incident: Incident, user: User, custom_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtener contexto para la plantilla"""
        context = {
            'INC_CODE': incident.code,
            'FECHA_DETECCION': incident.fecha_deteccion.strftime('%d/%m/%Y'),
            'HORA_DETECCION': incident.hora_deteccion.strftime('%H:%M'),
            'PROVEEDOR': incident.provider,
            'OBRA': incident.obra,
            'CLIENTE': incident.cliente,
            'CLIENTE_RUT': incident.cliente_rut,
            'DIRECCION': incident.direccion_cliente,
            'NUM_PEDIDO': incident.pedido_num,
            'NUM_FACTURA': incident.factura_num,
            'NC_NUMBER': incident.nc_number,
            'NP_NUMBER': incident.np_number,
            'SKU': incident.sku,
            'LOTE': incident.lote,
            'DESCRIPCION': incident.descripcion,
            'ACCIONES_INMEDIATAS': incident.acciones_inmediatas,
            'ACCIONES_POSTERIORES': getattr(incident, 'acciones_posteriores', ''),
            'ANALISIS_IA': self._format_ai_analysis(incident.ai_analysis),
            'CONCLUSIONES_TECNICAS': self._get_conclusiones_tecnicas(incident),
            'RECOMENDACIONES': self._get_recomendaciones(incident),
            'FIRMANTE': user.get_full_name() or user.username,
            'FIRMA_CARGO': self._get_user_role_display(user.role),
            'ANEXOS_FOTOS': incident.get_photos_list(),
            'FECHA_FIRMA': incident.updated_at.strftime('%d/%m/%Y'),
            'EXPERTO': self._get_expert_name(incident),
            'ENSAYOS': self._get_ensayos(incident),
            'OBSERVACIONES': self._get_observaciones(incident),
            'RESULTADOS': self._get_resultados(incident),
            'CONCLUSIONES': self._get_conclusiones(incident),
        }
        
        # Agregar datos personalizados
        if custom_data:
            context.update(custom_data)
        
        return context
    
    def _format_ai_analysis(self, ai_analysis: Optional[Dict[str, Any]]) -> str:
        """Formatear análisis de IA para el documento"""
        if not ai_analysis:
            return "No se realizó análisis de IA"
        
        try:
            analysis_text = []
            
            if 'caption' in ai_analysis:
                analysis_text.append(f"Descripción: {ai_analysis['caption']}")
            
            if 'suggested_causes' in ai_analysis:
                causes = ai_analysis['suggested_causes']
                if isinstance(causes, list) and causes:
                    analysis_text.append("Causas sugeridas:")
                    for i, cause in enumerate(causes[:3], 1):
                        confidence = cause.get('confidence', 0)
                        analysis_text.append(f"{i}. {cause.get('cause', 'Causa no especificada')} (Confianza: {confidence:.1%})")
            
            if 'recommendations' in ai_analysis:
                recommendations = ai_analysis['recommendations']
                if isinstance(recommendations, list) and recommendations:
                    analysis_text.append("Recomendaciones:")
                    for i, rec in enumerate(recommendations, 1):
                        analysis_text.append(f"{i}. {rec}")
            
            return "\n".join(analysis_text) if analysis_text else "Análisis de IA no disponible"
            
        except Exception as e:
            return f"Error formateando análisis de IA: {str(e)}"
    
    def _get_conclusiones_tecnicas(self, incident: Incident) -> str:
        """Obtener conclusiones técnicas del incidente"""
        # Buscar en reportes de laboratorio
        lab_reports = incident.lab_reports.all()
        if lab_reports.exists():
            latest_report = lab_reports.first()
            return latest_report.conclusions or "Conclusiones técnicas pendientes"
        
        # Buscar en análisis de IA
        if incident.ai_analysis:
            return self._format_ai_analysis(incident.ai_analysis)
        
        return "Conclusiones técnicas pendientes"
    
    def _get_recomendaciones(self, incident: Incident) -> str:
        """Obtener recomendaciones del incidente"""
        # Buscar en reportes de laboratorio
        lab_reports = incident.lab_reports.all()
        if lab_reports.exists():
            latest_report = lab_reports.first()
            return latest_report.conclusions or "Recomendaciones pendientes"
        
        # Recomendaciones por defecto basadas en el tipo de incidencia
        recommendations = {
            'defecto_fabricacion': "Revisar proceso de fabricación y implementar controles de calidad adicionales",
            'daño_transporte': "Mejorar embalaje y condiciones de transporte",
            'calidad': "Implementar inspecciones adicionales de calidad",
            'embalaje': "Revisar especificaciones de embalaje",
            'etiquetado': "Verificar proceso de etiquetado",
        }
        
        return recommendations.get(incident.categoria, "Recomendaciones pendientes")
    
    def _get_user_role_display(self, role: str) -> str:
        """Obtener nombre del rol para mostrar"""
        role_display = {
            'admin': 'Administrador',
            'supervisor': 'Supervisor',
            'analista': 'Analista Técnico',
            'atencion_cliente': 'Atención al Cliente',
            'proveedor': 'Proveedor',
        }
        return role_display.get(role, role.title())
    
    def _get_expert_name(self, incident: Incident) -> str:
        """Obtener nombre del experto"""
        lab_reports = incident.lab_reports.all()
        if lab_reports.exists():
            return lab_reports.first().expert_name
        return "Experto Técnico"
    
    def _get_ensayos(self, incident: Incident) -> str:
        """Obtener ensayos realizados"""
        lab_reports = incident.lab_reports.all()
        if lab_reports.exists():
            tests = lab_reports.first().tests_performed
            if isinstance(tests, list):
                return "\n".join([f"- {test}" for test in tests])
        return "Ensayos pendientes"
    
    def _get_observaciones(self, incident: Incident) -> str:
        """Obtener observaciones"""
        lab_reports = incident.lab_reports.all()
        if lab_reports.exists():
            return lab_reports.first().observations
        return "Observaciones pendientes"
    
    def _get_resultados(self, incident: Incident) -> str:
        """Obtener resultados"""
        lab_reports = incident.lab_reports.all()
        if lab_reports.exists():
            return lab_reports.first().conclusions
        return "Resultados pendientes"
    
    def _get_conclusiones(self, incident: Incident) -> str:
        """Obtener conclusiones"""
        return self._get_conclusiones_tecnicas(incident)


class ClienteInformeTemplate(DocumentTemplate):
    """Plantilla para informe de cliente (tono sutil y diplomático)"""
    
    def __init__(self):
        super().__init__("cliente_informe", "cliente_informe")
    
    def get_template_content(self) -> str:
        """Obtener contenido de la plantilla"""
        return """
INFORME DE INCIDENCIA POSTVENTA
{{INC_CODE}}

Estimado/a {{CLIENTE}},

En atención a su comunicación del {{FECHA_DETECCION}} a las {{HORA_DETECCION}}, realizamos una verificación técnica del elemento reportado. A continuación, presentamos los hallazgos y acciones propuestas:

INFORMACIÓN DE LA INCIDENCIA
─────────────────────────────────────────────────────────────
Código de Incidencia: {{INC_CODE}}
Fecha de Detección: {{FECHA_DETECCION}}
Hora de Detección: {{HORA_DETECCION}}
Proveedor: {{PROVEEDOR}}
Obra/Proyecto: {{OBRA}}
Cliente: {{CLIENTE}}
RUT: {{CLIENTE_RUT}}
Dirección: {{DIRECCION}}
Número de Pedido: {{NUM_PEDIDO}}
Número de Factura: {{NUM_FACTURA}}
SKU: {{SKU}}
Lote: {{LOTE}}

DESCRIPCIÓN DEL PROBLEMA
─────────────────────────────────────────────────────────────
{{DESCRIPCION}}

ACCIONES INMEDIATAS ADOPTADAS
─────────────────────────────────────────────────────────────
{{ACCIONES_INMEDIATAS}}

ANÁLISIS TÉCNICO
─────────────────────────────────────────────────────────────
{{ANALISIS_IA}}

CONCLUSIONES TÉCNICAS
─────────────────────────────────────────────────────────────
{{CONCLUSIONES_TECNICAS}}

RECOMENDACIONES
─────────────────────────────────────────────────────────────
{{RECOMENDACIONES}}

DOCUMENTACIÓN ANEXA
─────────────────────────────────────────────────────────────
{{ANEXOS_FOTOS}}

Agradecemos su comunicación y quedamos disponibles para coordinar las acciones de seguimiento que sean necesarias.

Atentamente,

{{FIRMANTE}}
{{FIRMA_CARGO}}
Fecha: {{FECHA_FIRMA}}

─────────────────────────────────────────────────────────────
NOTA: Este informe ha sido generado automáticamente por el Sistema de Gestión de Incidencias Postventa.
        """
    
    def get_context(self, incident: Incident, user: User, custom_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtener contexto con tono diplomático"""
        context = super().get_context(incident, user, custom_data)
        
        # Ajustar tono para cliente (evitar lenguaje acusatorio)
        if context['DESCRIPCION']:
            context['DESCRIPCION'] = self._soften_language(context['DESCRIPCION'])
        
        if context['CONCLUSIONES_TECNICAS']:
            context['CONCLUSIONES_TECNICAS'] = self._soften_language(context['CONCLUSIONES_TECNICAS'])
        
        return context
    
    def _soften_language(self, text: str) -> str:
        """Suavizar lenguaje para cliente"""
        replacements = {
            'falla': 'situación observada',
            'defecto': 'característica no conforme',
            'error': 'discrepancia',
            'problema': 'situación',
            'mal funcionamiento': 'funcionamiento no conforme',
            'daño': 'alteración',
            'rotura': 'fisura',
            'grieta': 'discontinuidad',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text


class ProveedorCartaTemplate(DocumentTemplate):
    """Plantilla para carta técnica a proveedor (tono directo y técnico)"""
    
    def __init__(self):
        super().__init__("proveedor_carta", "proveedor_carta")
    
    def get_template_content(self) -> str:
        """Obtener contenido de la plantilla"""
        return """
CARTA TÉCNICA - SOLICITUD DE REVISIÓN
{{INC_CODE}}

Estimados,

Adjuntamos evidencia correspondiente a la incidencia {{INC_CODE}} reportada por nuestro cliente {{CLIENTE}}.

INFORMACIÓN DE LA INCIDENCIA
─────────────────────────────────────────────────────────────
Código de Incidencia: {{INC_CODE}}
Fecha de Detección: {{FECHA_DETECCION}}
Hora de Detección: {{HORA_DETECCION}}
Proveedor: {{PROVEEDOR}}
Obra/Proyecto: {{OBRA}}
Cliente: {{CLIENTE}}
RUT Cliente: {{CLIENTE_RUT}}
Dirección Cliente: {{DIRECCION}}
Número de Pedido: {{NUM_PEDIDO}}
Número de Factura: {{NUM_FACTURA}}
SKU: {{SKU}}
Lote: {{LOTE}}

DESCRIPCIÓN TÉCNICA DEL PROBLEMA
─────────────────────────────────────────────────────────────
{{DESCRIPCION}}

ACCIONES INMEDIATAS ADOPTADAS
─────────────────────────────────────────────────────────────
{{ACCIONES_INMEDIATAS}}

ANÁLISIS TÉCNICO REALIZADO
─────────────────────────────────────────────────────────────
{{ANALISIS_IA}}

CONCLUSIONES TÉCNICAS
─────────────────────────────────────────────────────────────
{{CONCLUSIONES_TECNICAS}}

EVIDENCIA FOTOGRÁFICA
─────────────────────────────────────────────────────────────
{{ANEXOS_FOTOS}}

SOLICITUD DE ACCIONES
─────────────────────────────────────────────────────────────
Solicitamos su revisión del proceso de fabricación y la entrega de un plan de acciones correctivas y preventivas para evitar la recurrencia de esta situación.

Específicamente, requerimos:

1. Análisis de la causa raíz del problema identificado
2. Plan de acciones correctivas para el lote afectado
3. Plan de acciones preventivas para futuros lotes
4. Propuesta de mejora en el proceso de fabricación
5. Coordinación para envío de muestras para ensayos complementarios

REFERENCIAS
─────────────────────────────────────────────────────────────
NC Number: {{NC_NUMBER}}
NP Number: {{NP_NUMBER}}

Plazo de respuesta solicitado: 15 días hábiles

Quedamos a la espera de su respuesta y disponibilidad para coordinar las acciones necesarias.

Saludos cordiales,

{{FIRMANTE}}
{{FIRMA_CARGO}}
Fecha: {{FECHA_FIRMA}}

─────────────────────────────────────────────────────────────
NOTA: Este documento ha sido generado automáticamente por el Sistema de Gestión de Incidencias Postventa.
        """


class LabReportTemplate(DocumentTemplate):
    """Plantilla para reporte de laboratorio"""
    
    def __init__(self):
        super().__init__("lab_report", "lab_report")
    
    def get_template_content(self) -> str:
        """Obtener contenido de la plantilla"""
        return """
REPORTE DE LABORATORIO
{{INC_CODE}}

INFORMACIÓN DE LA MUESTRA
─────────────────────────────────────────────────────────────
Código de Incidencia: {{INC_CODE}}
Fecha de Recepción: {{FECHA_DETECCION}}
Cliente: {{CLIENTE}}
Proveedor: {{PROVEEDOR}}
Obra/Proyecto: {{OBRA}}
SKU: {{SKU}}
Lote: {{LOTE}}
Número de Pedido: {{NUM_PEDIDO}}

DESCRIPCIÓN DE LA MUESTRA
─────────────────────────────────────────────────────────────
{{DESCRIPCION}}

ENSAYOS REALIZADOS
─────────────────────────────────────────────────────────────
{{ENSAYOS}}

OBSERVACIONES TÉCNICAS
─────────────────────────────────────────────────────────────
{{OBSERVACIONES}}

RESULTADOS DE ENSAYOS
─────────────────────────────────────────────────────────────
{{RESULTADOS}}

ANÁLISIS DE IA
─────────────────────────────────────────────────────────────
{{ANALISIS_IA}}

CONCLUSIONES TÉCNICAS
─────────────────────────────────────────────────────────────
{{CONCLUSIONES}}

RECOMENDACIONES
─────────────────────────────────────────────────────────────
{{RECOMENDACIONES}}

EVIDENCIA FOTOGRÁFICA
─────────────────────────────────────────────────────────────
{{ANEXOS_FOTOS}}

FIRMA DEL EXPERTO
─────────────────────────────────────────────────────────────
{{EXPERTO}}
Laboratorio de Control de Calidad
Fecha: {{FECHA_FIRMA}}

─────────────────────────────────────────────────────────────
NOTA: Este reporte ha sido generado automáticamente por el Sistema de Gestión de Incidencias Postventa.
        """


class DocumentTemplateManager:
    """Gestor de plantillas de documentos"""
    
    def __init__(self):
        self.templates = {
            'cliente_informe': ClienteInformeTemplate(),
            'proveedor_carta': ProveedorCartaTemplate(),
            'lab_report': LabReportTemplate(),
        }
    
    def get_template(self, template_type: str) -> Optional[DocumentTemplate]:
        """Obtener plantilla por tipo"""
        return self.templates.get(template_type)
    
    def get_available_templates(self) -> Dict[str, str]:
        """Obtener plantillas disponibles"""
        return {
            'cliente_informe': 'Informe para Cliente',
            'proveedor_carta': 'Carta Técnica para Proveedor',
            'lab_report': 'Reporte de Laboratorio',
        }
    
    def generate_document_content(self, template_type: str, incident: Incident, user: User, custom_data: Dict[str, Any] = None) -> str:
        """Generar contenido del documento"""
        template = self.get_template(template_type)
        if not template:
            raise ValueError(f"Plantilla {template_type} no encontrada")
        
        context = template.get_context(incident, user, custom_data)
        content = template.get_template_content()
        
        # Reemplazar placeholders
        for placeholder, value in context.items():
            content = content.replace(f"{{{{{placeholder}}}}}", str(value or ''))
        
        return content


# Instancia global del gestor de plantillas
template_manager = DocumentTemplateManager()
