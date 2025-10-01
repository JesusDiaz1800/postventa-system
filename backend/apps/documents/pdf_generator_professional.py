"""
Generador de PDFs profesionales con logo de Polifusion
"""
import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from django.conf import settings

logger = logging.getLogger(__name__)

class ProfessionalPDFGenerator:
    """Generador de PDFs profesionales con logo de Polifusion"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.logo_path = self.get_logo_path()
    
    def get_logo_path(self):
        """Obtiene la ruta del logo de Polifusion"""
        # Buscar logo en diferentes ubicaciones
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'images', 'polifusion_logo.png'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'polifusion_logo.jpg'),
            os.path.join(settings.BASE_DIR, 'media', 'polifusion_logo.png'),
            os.path.join(settings.BASE_DIR, 'media', 'polifusion_logo.jpg'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Si no se encuentra, crear un logo simple
        return None
    
    def setup_custom_styles(self):
        """Configura estilos personalizados"""
        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#1e40af'),  # Azul Polifusion
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=HexColor('#374151'),  # Gris oscuro
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Estilo para información de la empresa
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_CENTER,
            textColor=HexColor('#6b7280'),  # Gris medio
            fontName='Helvetica'
        ))
    
    def create_header(self, story, title, subtitle=None):
        """Crea el encabezado del documento"""
        # Logo de Polifusion
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=2*inch, height=1*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                logger.warning(f"No se pudo cargar el logo: {e}")
        
        # Título principal
        story.append(Paragraph(title, self.styles['CustomTitle']))
        
        # Subtítulo si se proporciona
        if subtitle:
            story.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        
        # Información de la empresa
        company_info = [
            "POLIFUSION S.A.",
            "Sistema de Gestión de Postventa",
            f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ]
        
        for info in company_info:
            story.append(Paragraph(info, self.styles['CompanyInfo']))
        
        story.append(Spacer(1, 0.3*inch))
    
    def create_visit_report_pdf(self, report_data, output_path):
        """Genera PDF profesional para reporte de visita"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Encabezado
            self.create_header(
                story, 
                "REPORTE DE VISITA TÉCNICA",
                f"Número: {report_data.get('report_number', 'N/A')}"
            )
            
            # Información general
            general_info = [
                ['Cliente:', report_data.get('client_name', 'N/A')],
                ['Proyecto:', report_data.get('project_name', 'N/A')],
                ['Fecha de Visita:', report_data.get('visit_date', 'N/A')],
                ['Técnico Responsable:', report_data.get('technician', 'N/A')],
                ['Dirección:', report_data.get('address', 'N/A')],
                ['Comuna:', report_data.get('commune', 'N/A')],
                ['Ciudad:', report_data.get('city', 'N/A')],
            ]
            
            story.append(Paragraph("INFORMACIÓN GENERAL", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 0.1*inch))
            
            table = Table(general_info, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
            
            # Motivo de la visita
            if report_data.get('visit_reason'):
                story.append(Paragraph("MOTIVO DE LA VISITA", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['visit_reason'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Observaciones
            if report_data.get('general_observations'):
                story.append(Paragraph("OBSERVACIONES GENERALES", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['general_observations'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Información de la incidencia relacionada
            if report_data.get('incident'):
                story.append(Paragraph("INCIDENCIA RELACIONADA", self.styles['CustomSubtitle']))
                incident_info = [
                    ['Código:', report_data['incident'].get('codigo', 'N/A')],
                    ['Cliente:', report_data['incident'].get('cliente', 'N/A')],
                    ['Producto:', report_data['incident'].get('producto', 'N/A')],
                    ['Descripción:', report_data['incident'].get('descripcion', 'N/A')],
                ]
                
                incident_table = Table(incident_info, colWidths=[1.5*inch, 4.5*inch])
                incident_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), HexColor('#fef3c7')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(incident_table)
            
            # Pie de página
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("Este documento ha sido generado automáticamente por el Sistema de Gestión de Postventa de Polifusion S.A.", self.styles['CompanyInfo']))
            
            doc.build(story)
            return True
            
        except Exception as e:
            logger.error(f"Error generando PDF de reporte de visita: {str(e)}", exc_info=True)
            return False
    
    def create_lab_report_pdf(self, report_data, output_path):
        """Genera PDF profesional para reporte de laboratorio"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Encabezado
            self.create_header(
                story, 
                "REPORTE DE LABORATORIO",
                f"Número: {report_data.get('report_number', 'N/A')}"
            )
            
            # Información general
            general_info = [
                ['Número de Formulario:', report_data.get('form_number', 'N/A')],
                ['Fecha de Solicitud:', report_data.get('request_date', 'N/A')],
                ['Solicitante:', report_data.get('applicant', 'N/A')],
                ['Cliente:', report_data.get('client', 'N/A')],
                ['Tipo de Reporte:', report_data.get('report_type', 'N/A')],
            ]
            
            story.append(Paragraph("INFORMACIÓN GENERAL", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 0.1*inch))
            
            table = Table(general_info, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
            
            # Descripción del análisis
            if report_data.get('description'):
                story.append(Paragraph("DESCRIPCIÓN DEL ANÁLISIS", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['description'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Antecedentes del proyecto
            if report_data.get('project_background'):
                story.append(Paragraph("ANTECEDENTES DEL PROYECTO", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['project_background'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Pruebas realizadas
            if report_data.get('tests_performed'):
                story.append(Paragraph("PRUEBAS REALIZADAS", self.styles['CustomSubtitle']))
                tests_data = report_data['tests_performed']
                if isinstance(tests_data, dict):
                    test_items = []
                    for test_name, result in tests_data.items():
                        test_items.append([test_name.replace('_', ' ').title(), str(result)])
                    
                    if test_items:
                        test_table = Table(test_items, colWidths=[3*inch, 3*inch])
                        test_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), HexColor('#fef3c7')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ('TOPPADDING', (0, 0), (-1, -1), 6),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(test_table)
                story.append(Spacer(1, 0.2*inch))
            
            # Comentarios
            if report_data.get('comments'):
                story.append(Paragraph("COMENTARIOS", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['comments'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Conclusiones
            if report_data.get('conclusions'):
                story.append(Paragraph("CONCLUSIONES", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['conclusions'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Recomendaciones
            if report_data.get('recommendations'):
                story.append(Paragraph("RECOMENDACIONES", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['recommendations'], self.styles['CustomNormal']))
            
            # Pie de página
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("Este documento ha sido generado automáticamente por el Sistema de Gestión de Postventa de Polifusion S.A.", self.styles['CompanyInfo']))
            
            doc.build(story)
            return True
            
        except Exception as e:
            logger.error(f"Error generando PDF de reporte de laboratorio: {str(e)}", exc_info=True)
            return False
    
    def create_supplier_report_pdf(self, report_data, output_path):
        """Genera PDF profesional para reporte de proveedor"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Encabezado
            self.create_header(
                story, 
                "INFORME PARA PROVEEDOR",
                f"Número: {report_data.get('report_number', 'N/A')}"
            )
            
            # Información del proveedor
            supplier_info = [
                ['Proveedor:', report_data.get('supplier_name', 'N/A')],
                ['Contacto:', report_data.get('supplier_contact', 'N/A')],
                ['Email:', report_data.get('supplier_email', 'N/A')],
                ['Fecha del Informe:', report_data.get('report_date', 'N/A')],
                ['Asunto:', report_data.get('subject', 'N/A')],
            ]
            
            story.append(Paragraph("INFORMACIÓN DEL PROVEEDOR", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 0.1*inch))
            
            table = Table(supplier_info, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
            
            # Introducción
            if report_data.get('introduction'):
                story.append(Paragraph("INTRODUCCIÓN", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['introduction'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Descripción del problema
            if report_data.get('problem_description'):
                story.append(Paragraph("DESCRIPCIÓN DEL PROBLEMA", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['problem_description'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Análisis técnico
            if report_data.get('technical_analysis'):
                story.append(Paragraph("ANÁLISIS TÉCNICO", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['technical_analysis'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Recomendaciones
            if report_data.get('recommendations'):
                story.append(Paragraph("RECOMENDACIONES", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['recommendations'], self.styles['CustomNormal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Mejoras esperadas
            if report_data.get('expected_improvements'):
                story.append(Paragraph("MEJORAS ESPERADAS", self.styles['CustomSubtitle']))
                story.append(Paragraph(report_data['expected_improvements'], self.styles['CustomNormal']))
            
            # Pie de página
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("Este documento ha sido generado automáticamente por el Sistema de Gestión de Postventa de Polifusion S.A.", self.styles['CompanyInfo']))
            
            doc.build(story)
            return True
            
        except Exception as e:
            logger.error(f"Error generando PDF de reporte de proveedor: {str(e)}", exc_info=True)
            return False
