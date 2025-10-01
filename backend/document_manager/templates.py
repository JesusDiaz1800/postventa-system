"""
Gestor de plantillas para documentos
Maneja plantillas HTML y Word para generación de documentos
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TemplateManager:
    """
    Gestor de plantillas para documentos
    """
    
    def __init__(self, templates_path: str = None):
        """
        Inicializar gestor de plantillas
        
        Args:
            templates_path: Ruta de las plantillas
        """
        self.templates_path = templates_path or os.path.join(os.getcwd(), 'document_manager', 'templates')
        self._create_templates()
        
        logger.info(f"TemplateManager inicializado en: {self.templates_path}")
    
    def _create_templates(self):
        """Crear plantillas base si no existen"""
        os.makedirs(self.templates_path, exist_ok=True)
        
        # Crear plantilla de informe de incidencia
        self._create_incident_report_template()
        self._create_visit_report_template()
        self._create_lab_report_template()
        self._create_supplier_report_template()
    
    def _create_incident_report_template(self):
        """Crear plantilla de informe de incidencia"""
        template_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Informe de Incidencia - {{incident_code}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { background-color: #126FCC; color: white; padding: 20px; text-align: center; }
        .content { margin: 20px 0; }
        .section { margin: 20px 0; border-left: 4px solid #126FCC; padding-left: 15px; }
        .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .table th { background-color: #f5f5f5; font-weight: bold; }
        .footer { margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 10px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>INFORME DE INCIDENCIA</h1>
        <h2>{{incident_code}} - {{client_name}}</h2>
    </div>
    
    <div class="content">
        <div class="section">
            <h3>Información General</h3>
            <table class="table">
                <tr><th>Número de Incidencia:</th><td>{{incident_code}}</td></tr>
                <tr><th>Cliente:</th><td>{{client_name}}</td></tr>
                <tr><th>Proyecto:</th><td>{{project_name}}</td></tr>
                <tr><th>Fecha de Detección:</th><td>{{detection_date}}</td></tr>
                <tr><th>Prioridad:</th><td>{{priority}}</td></tr>
                <tr><th>Responsable:</th><td>{{responsible}}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>Descripción del Problema</h3>
            <p>{{description}}</p>
        </div>
        
        <div class="section">
            <h3>Información del Producto</h3>
            <table class="table">
                <tr><th>Categoría:</th><td>{{product_category}}</td></tr>
                <tr><th>Subcategoría:</th><td>{{product_subcategory}}</td></tr>
                <tr><th>SKU:</th><td>{{product_sku}}</td></tr>
                <tr><th>Lote:</th><td>{{product_lot}}</td></tr>
                <tr><th>Proveedor:</th><td>{{product_provider}}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>Acciones Tomadas</h3>
            <p>{{actions_taken}}</p>
        </div>
        
        <div class="section">
            <h3>Recomendaciones</h3>
            <p>{{recommendations}}</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Documento generado el {{generation_date}} por {{generated_by}}</p>
        <p>Polifusión S.A. - Sistema de Control de Calidad</p>
    </div>
</body>
</html>
        """
        
        template_path = os.path.join(self.templates_path, 'incident_report.html')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def _create_visit_report_template(self):
        """Crear plantilla de informe de visita"""
        template_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Informe de Visita Técnica - {{order_number}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { background-color: #126FCC; color: white; padding: 20px; text-align: center; }
        .content { margin: 20px 0; }
        .section { margin: 20px 0; border-left: 4px solid #126FCC; padding-left: 15px; }
        .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .table th { background-color: #f5f5f5; font-weight: bold; }
        .footer { margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 10px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>INFORME DE VISITA TÉCNICA</h1>
        <h2>{{order_number}} - {{client_name}}</h2>
    </div>
    
    <div class="content">
        <div class="section">
            <h3>Información de la Visita</h3>
            <table class="table">
                <tr><th>Número de Orden:</th><td>{{order_number}}</td></tr>
                <tr><th>Cliente:</th><td>{{client_name}}</td></tr>
                <tr><th>Proyecto:</th><td>{{project_name}}</td></tr>
                <tr><th>Dirección:</th><td>{{address}}</td></tr>
                <tr><th>Fecha de Visita:</th><td>{{visit_date}}</td></tr>
                <tr><th>Técnico:</th><td>{{technician}}</td></tr>
                <tr><th>Vendedor:</th><td>{{salesperson}}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>Observaciones Generales</h3>
            <p>{{general_observations}}</p>
        </div>
        
        <div class="section">
            <h3>Observaciones Técnicas</h3>
            <h4>Muro:</h4>
            <p>{{wall_observations}}</p>
            <h4>Matriz:</h4>
            <p>{{matrix_observations}}</p>
            <h4>Losa:</h4>
            <p>{{slab_observations}}</p>
            <h4>Almacenamiento:</h4>
            <p>{{storage_observations}}</p>
        </div>
        
        <div class="section">
            <h3>Datos de Máquinas</h3>
            {{machine_data_table}}
        </div>
    </div>
    
    <div class="footer">
        <p>Documento generado el {{generation_date}} por {{generated_by}}</p>
        <p>Polifusión S.A. - Sistema de Control de Calidad</p>
    </div>
</body>
</html>
        """
        
        template_path = os.path.join(self.templates_path, 'visit_report.html')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def _create_lab_report_template(self):
        """Crear plantilla de informe de laboratorio"""
        template_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Informe de Laboratorio - {{report_number}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { background-color: #126FCC; color: white; padding: 20px; text-align: center; }
        .content { margin: 20px 0; }
        .section { margin: 20px 0; border-left: 4px solid #126FCC; padding-left: 15px; }
        .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .table th { background-color: #f5f5f5; font-weight: bold; }
        .footer { margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 10px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>INFORME DE LABORATORIO</h1>
        <h2>{{report_number}} - {{client}}</h2>
    </div>
    
    <div class="content">
        <div class="section">
            <h3>Información del Análisis</h3>
            <table class="table">
                <tr><th>Número de Reporte:</th><td>{{report_number}}</td></tr>
                <tr><th>Cliente:</th><td>{{client}}</td></tr>
                <tr><th>Fecha de Solicitud:</th><td>{{request_date}}</td></tr>
                <tr><th>Experto Técnico:</th><td>{{technical_expert_name}}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>Antecedentes del Proyecto</h3>
            <p>{{project_background}}</p>
        </div>
        
        <div class="section">
            <h3>Ensayos Realizados</h3>
            {{tests_performed_table}}
        </div>
        
        <div class="section">
            <h3>Comentarios</h3>
            <p>{{comments}}</p>
        </div>
        
        <div class="section">
            <h3>Conclusiones</h3>
            <p>{{conclusions}}</p>
        </div>
        
        <div class="section">
            <h3>Recomendaciones</h3>
            <p>{{recommendations}}</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Documento generado el {{generation_date}} por {{generated_by}}</p>
        <p>Polifusión S.A. - Sistema de Control de Calidad</p>
    </div>
</body>
</html>
        """
        
        template_path = os.path.join(self.templates_path, 'lab_report.html')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def _create_supplier_report_template(self):
        """Crear plantilla de informe de proveedor"""
        template_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Informe para Proveedor - {{report_number}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { background-color: #126FCC; color: white; padding: 20px; text-align: center; }
        .content { margin: 20px 0; }
        .section { margin: 20px 0; border-left: 4px solid #126FCC; padding-left: 15px; }
        .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .table th { background-color: #f5f5f5; font-weight: bold; }
        .footer { margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 10px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>INFORME PARA PROVEEDOR</h1>
        <h2>{{report_number}} - {{supplier_name}}</h2>
    </div>
    
    <div class="content">
        <div class="section">
            <h3>Información del Proveedor</h3>
            <table class="table">
                <tr><th>Proveedor:</th><td>{{supplier_name}}</td></tr>
                <tr><th>Contacto:</th><td>{{supplier_contact}}</td></tr>
                <tr><th>Email:</th><td>{{supplier_email}}</td></tr>
                <tr><th>Asunto:</th><td>{{subject}}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h3>Introducción</h3>
            <p>{{introduction}}</p>
        </div>
        
        <div class="section">
            <h3>Descripción del Problema</h3>
            <p>{{problem_description}}</p>
        </div>
        
        <div class="section">
            <h3>Análisis Técnico</h3>
            <p>{{technical_analysis}}</p>
        </div>
        
        <div class="section">
            <h3>Recomendaciones</h3>
            <p>{{recommendations}}</p>
        </div>
        
        <div class="section">
            <h3>Mejoras Esperadas</h3>
            <p>{{expected_improvements}}</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Documento generado el {{generation_date}} por {{generated_by}}</p>
        <p>Polifusión S.A. - Sistema de Control de Calidad</p>
    </div>
</body>
</html>
        """
        
        template_path = os.path.join(self.templates_path, 'supplier_report.html')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_path)
    
    def get_template(self, template_name: str, format_type: str = "html") -> str:
        """
        Obtener ruta de plantilla
        
        Args:
            template_name: Nombre de la plantilla
            format_type: Tipo de formato (html, docx)
            
        Returns:
            Ruta de la plantilla
        """
        template_path = os.path.join(self.templates_path, f"{template_name}.{format_type}")
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
        
        return template_path
    
    def render_template(self, template_name: str, contexto: Dict[str, Any]) -> str:
        """
        Renderizar plantilla con contexto
        
        Args:
            template_name: Nombre de la plantilla
            contexto: Datos para la plantilla
            
        Returns:
            Contenido renderizado
        """
        template_path = self.get_template(template_name, "html")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Renderizar con Jinja2
        from jinja2 import Template
        template = Template(template_content)
        return template.render(**contexto)
    
    def create_custom_template(self, template_name: str, content: str, format_type: str = "html") -> str:
        """
        Crear plantilla personalizada
        
        Args:
            template_name: Nombre de la plantilla
            content: Contenido de la plantilla
            format_type: Tipo de formato
            
        Returns:
            Ruta de la plantilla creada
        """
        template_path = os.path.join(self.templates_path, f"{template_name}.{format_type}")
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Plantilla personalizada creada: {template_path}")
        return template_path
