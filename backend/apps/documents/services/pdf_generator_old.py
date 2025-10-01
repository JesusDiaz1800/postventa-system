import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
import logging
from .professional_pdf_generator import ProfessionalPDFGenerator

logger = logging.getLogger(__name__)

class ProfessionalPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e40af')
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#374151')
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Estilo para encabezados de tabla
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        ))

    def add_header(self, canvas, doc):
        """Agregar encabezado con logo de Polifusion"""
        canvas.saveState()
        
        # Logo (si existe)
        logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'polifusion_logo.png')
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 50, 750, width=100, height=50)
        
        # Información de la empresa
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.HexColor('#1e40af'))
        canvas.drawString(200, 780, "POLIFUSIÓN S.A.")
        
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.black)
        canvas.drawString(200, 760, "Cacique Collin 2525 Lampa")
        
        # Fecha actual
        canvas.setFont('Helvetica', 10)
        canvas.drawString(450, 780, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        
        canvas.restoreState()

    def add_footer(self, canvas, doc):
        """Agregar pie de página"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(50, 50, f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}")
        canvas.drawRightString(550, 50, f"Página {doc.page}")
        canvas.restoreState()

    def generate_visit_report_pdf(self, report_data, images=None):
        """Generar PDF profesional para reporte de visita"""
        professional_generator = ProfessionalPDFGenerator()
        return professional_generator.generate_visit_report_pdf(report_data)
        
        story = []
        
        # Título principal
        story.append(Paragraph("REPORTE VISITA", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Información básica
        story.append(Paragraph("INFORMACIÓN BÁSICA", self.styles['CustomSubtitle']))
        
        basic_info = [
            ['Fecha Visita:', report_data.get('visit_date', '')],
            ['Orden N°:', report_data.get('order_number', '')],
            ['Proyecto:', report_data.get('project_name', '')],
            ['Cliente:', report_data.get('client_name', '')],
            ['Dirección:', report_data.get('address', '')],
            ['Comuna:', report_data.get('commune', '')],
            ['Ciudad:', report_data.get('city', '')],
            ['Motivo Visita:', report_data.get('visit_reason', '')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Personal involucrado
        story.append(Paragraph("PERSONAL INVOLUCRADO", self.styles['CustomSubtitle']))
        
        personnel_info = [
            ['Vendedor:', report_data.get('salesperson', '')],
            ['Técnico:', report_data.get('technician', '')],
            ['Instalador:', report_data.get('installer', '')],
            ['Teléfono Instalador:', report_data.get('installer_phone', '')],
            ['Empresa Constructora:', report_data.get('construction_company', '')]
        ]
        
        personnel_table = Table(personnel_info, colWidths=[2*inch, 4*inch])
        personnel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(personnel_table)
        story.append(Spacer(1, 20))
        
        # Datos de máquinas
        machine_data = report_data.get('machine_data', {})
        if isinstance(machine_data, str):
            try:
                import json
                machine_data = json.loads(machine_data)
            except:
                machine_data = {}
        
        if machine_data.get('machines'):
            story.append(Paragraph("DATOS DE MÁQUINAS", self.styles['CustomSubtitle']))
            
            machine_headers = ['Máquina', 'Inicio', 'Corte']
            machine_table_data = [machine_headers]
            
            for machine in machine_data.get('machines', []):
                machine_table_data.append([
                    machine.get('machine', ''),
                    machine.get('start', ''),
                    machine.get('cut', '')
                ])
            
            machine_table = Table(machine_table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            machine_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#faf5ff')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(machine_table)
            story.append(Spacer(1, 20))
        
        # Observaciones
        story.append(Paragraph("OBSERVACIONES", self.styles['CustomSubtitle']))
        
        observations = [
            ('Obs Muro/Tabique:', report_data.get('wall_observations', '')),
            ('Obs Matriz:', report_data.get('matrix_observations', '')),
            ('Obs Loza:', report_data.get('slab_observations', '')),
            ('Obs Almacenaje:', report_data.get('storage_observations', '')),
            ('Obs Pre Armados:', report_data.get('pre_assembled_observations', '')),
            ('Obs Exteriores:', report_data.get('exterior_observations', '')),
            ('Obs Generales:', report_data.get('general_observations', ''))
        ]
        
        for title, content in observations:
            if content.strip():
                story.append(Paragraph(f"<b>{title}</b>", self.styles['CustomBody']))
                story.append(Paragraph(content, self.styles['CustomBody']))
                story.append(Spacer(1, 10))
        
        # Imágenes (si las hay)
        if images:
            story.append(PageBreak())
            story.append(Paragraph("IMÁGENES DEL REPORTE", self.styles['CustomSubtitle']))
            
            for i, image_data in enumerate(images):
                try:
                    # Aquí se procesarían las imágenes subidas
                    story.append(Paragraph(f"Imagen {i+1}", self.styles['CustomBody']))
                    story.append(Spacer(1, 10))
                except Exception as e:
                    logger.error(f"Error procesando imagen {i+1}: {str(e)}")
        
        # Firmas
        story.append(Spacer(1, 30))
        story.append(Paragraph("FIRMAS", self.styles['CustomSubtitle']))
        
        signatures = [
            ['Firma Técnico:', '_________________________'],
            ['Firma Instalador:', '_________________________']
        ]
        
        signature_table = Table(signatures, colWidths=[2*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('GRID', (0, 0), (-1, -1), 0, colors.white)
        ]))
        
        story.append(signature_table)
        
        # Construir PDF
        doc.build(story, onFirstPage=self.add_header, onLaterPages=self.add_header)
        
        buffer.seek(0)
        return buffer.getvalue()

    def generate_lab_report_pdf(self, report_data, images=None):
        """Generar PDF profesional para reporte de laboratorio"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=100,
            bottomMargin=72
        )
        
        story = []
        
        # Título principal
        story.append(Paragraph("REPORTE DE LABORATORIO", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Información básica
        story.append(Paragraph("INFORMACIÓN BÁSICA", self.styles['CustomSubtitle']))
        
        basic_info = [
            ['Número de Reporte:', report_data.get('report_number', '')],
            ['Fecha del Reporte:', report_data.get('report_date', '')],
            ['Proyecto:', report_data.get('project_name', '')],
            ['Cliente:', report_data.get('client_name', '')],
            ['Dirección:', report_data.get('address', '')],
            ['Comuna:', report_data.get('commune', '')],
            ['Ciudad:', report_data.get('city', '')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#faf5ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Personal involucrado
        story.append(Paragraph("PERSONAL INVOLUCRADO", self.styles['CustomSubtitle']))
        
        personnel_info = [
            ['Técnico Responsable:', report_data.get('technician', '')],
            ['Supervisor:', report_data.get('supervisor', '')],
            ['Analista de Laboratorio:', report_data.get('lab_analyst', '')]
        ]
        
        personnel_table = Table(personnel_info, colWidths=[2*inch, 4*inch])
        personnel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(personnel_table)
        story.append(Spacer(1, 20))
        
        # Información de la muestra
        story.append(Paragraph("INFORMACIÓN DE LA MUESTRA", self.styles['CustomSubtitle']))
        
        sample_info = [
            ['Tipo de Análisis:', report_data.get('analysis_type', '')],
            ['Descripción:', report_data.get('sample_description', '')],
            ['Cantidad:', report_data.get('sample_quantity', '')],
            ['Condición:', report_data.get('sample_condition', '')]
        ]
        
        sample_table = Table(sample_info, colWidths=[2*inch, 4*inch])
        sample_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fef2f2')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(sample_table)
        story.append(Spacer(1, 20))
        
        # Parámetros de análisis
        if report_data.get('analysis_parameters'):
            story.append(Paragraph("PARÁMETROS DE ANÁLISIS", self.styles['CustomSubtitle']))
            
            params = report_data['analysis_parameters']
            param_info = [
                ['Temperatura (°C):', params.get('temperature', '')],
                ['Presión (atm):', params.get('pressure', '')],
                ['Humedad (%):', params.get('humidity', '')],
                ['Nivel de pH:', params.get('ph_level', '')],
                ['Conductividad (μS/cm):', params.get('conductivity', '')],
                ['Otros Parámetros:', params.get('other_parameters', '')]
            ]
            
            param_table = Table(param_info, colWidths=[2*inch, 4*inch])
            param_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ea580c')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fff7ed')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(param_table)
            story.append(Spacer(1, 20))
        
        # Resultados de pruebas
        if report_data.get('test_results'):
            story.append(Paragraph("RESULTADOS DE PRUEBAS", self.styles['CustomSubtitle']))
            
            results = report_data['test_results']
            test_results = [
                ('Inspección Visual:', results.get('visual_inspection', '')),
                ('Análisis Dimensional:', results.get('dimensional_analysis', '')),
                ('Pruebas Mecánicas:', results.get('mechanical_tests', '')),
                ('Análisis Químico:', results.get('chemical_analysis', '')),
                ('Otras Pruebas:', results.get('other_tests', ''))
            ]
            
            for title, content in test_results:
                if content.strip():
                    story.append(Paragraph(f"<b>{title}</b>", self.styles['CustomBody']))
                    story.append(Paragraph(content, self.styles['CustomBody']))
                    story.append(Spacer(1, 10))
        
        # Conclusiones y recomendaciones
        story.append(Paragraph("CONCLUSIONES Y RECOMENDACIONES", self.styles['CustomSubtitle']))
        
        conclusions = [
            ('Conclusiones:', report_data.get('conclusions', '')),
            ('Recomendaciones:', report_data.get('recommendations', '')),
            ('Estado de Cumplimiento:', report_data.get('compliance_status', ''))
        ]
        
        for title, content in conclusions:
            if content.strip():
                story.append(Paragraph(f"<b>{title}</b>", self.styles['CustomBody']))
                story.append(Paragraph(content, self.styles['CustomBody']))
                story.append(Spacer(1, 10))
        
        # Imágenes (si las hay)
        if images:
            story.append(PageBreak())
            story.append(Paragraph("IMÁGENES DEL REPORTE", self.styles['CustomSubtitle']))
            
            for i, image_data in enumerate(images):
                try:
                    story.append(Paragraph(f"Imagen {i+1}", self.styles['CustomBody']))
                    story.append(Spacer(1, 10))
                except Exception as e:
                    logger.error(f"Error procesando imagen {i+1}: {str(e)}")
        
        # Firmas
        story.append(Spacer(1, 30))
        story.append(Paragraph("FIRMAS", self.styles['CustomSubtitle']))
        
        signatures = [
            ['Firma Técnico:', '_________________________'],
            ['Firma Analista:', '_________________________'],
            ['Firma Supervisor:', '_________________________']
        ]
        
        signature_table = Table(signatures, colWidths=[2*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('GRID', (0, 0), (-1, -1), 0, colors.white)
        ]))
        
        story.append(signature_table)
        
        # Construir PDF
        doc.build(story, onFirstPage=self.add_header, onLaterPages=self.add_header)
        
        buffer.seek(0)
        return buffer.getvalue()

    def generate_supplier_report_pdf(self, report_data, images=None):
        """Generar PDF profesional para reporte de proveedor"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=100,
            bottomMargin=72
        )
        
        story = []
        
        # Título principal
        story.append(Paragraph("REPORTE DE PROVEEDOR", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Información básica
        story.append(Paragraph("INFORMACIÓN BÁSICA", self.styles['CustomSubtitle']))
        
        basic_info = [
            ['Fecha del Reporte:', report_data.get('report_date', '')],
            ['Proveedor:', report_data.get('supplier_name', '')],
            ['Contacto:', report_data.get('supplier_contact', '')],
            ['Email:', report_data.get('supplier_email', '')],
            ['Teléfono:', report_data.get('supplier_phone', '')],
            ['Dirección:', report_data.get('supplier_address', '')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Descripción del problema
        story.append(Paragraph("DESCRIPCIÓN DEL PROBLEMA", self.styles['CustomSubtitle']))
        story.append(Paragraph(report_data.get('issue_description', ''), self.styles['CustomBody']))
        story.append(Spacer(1, 20))
        
        # Respuesta del proveedor
        if report_data.get('supplier_response'):
            story.append(Paragraph("RESPUESTA DEL PROVEEDOR", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('supplier_response', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Acciones correctivas
        if report_data.get('corrective_actions'):
            story.append(Paragraph("ACCIONES CORRECTIVAS", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('corrective_actions', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Medidas preventivas
        if report_data.get('preventive_measures'):
            story.append(Paragraph("MEDIDAS PREVENTIVAS", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('preventive_measures', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Seguimiento
        if report_data.get('follow_up_required'):
            story.append(Paragraph("SEGUIMIENTO", self.styles['CustomSubtitle']))
            follow_up_info = [
                ['Requiere Seguimiento:', 'Sí'],
                ['Fecha de Seguimiento:', report_data.get('follow_up_date', 'No especificada')]
            ]
            
            follow_up_table = Table(follow_up_info, colWidths=[2*inch, 4*inch])
            follow_up_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fef2f2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(follow_up_table)
            story.append(Spacer(1, 20))
        
        # Imágenes (si las hay)
        if images:
            story.append(PageBreak())
            story.append(Paragraph("IMÁGENES DEL REPORTE", self.styles['CustomSubtitle']))
            
            for i, image_data in enumerate(images):
                try:
                    story.append(Paragraph(f"Imagen {i+1}", self.styles['CustomBody']))
                    story.append(Spacer(1, 10))
                except Exception as e:
                    logger.error(f"Error procesando imagen {i+1}: {str(e)}")
        
        # Construir PDF
        doc.build(story, onFirstPage=self.add_header, onLaterPages=self.add_header)
        
        buffer.seek(0)
        return buffer.getvalue()

    def generate_quality_report_pdf(self, report_data, images=None):
        """Generar PDF profesional para reporte de calidad"""
        professional_generator = ProfessionalPDFGenerator()
        return professional_generator.generate_quality_report_pdf(report_data)
        
        story = []
        
        # Título principal
        report_type = report_data.get('report_type', 'cliente')
        title = "REPORTE DE CALIDAD - PARA CLIENTE" if report_type == 'cliente' else "REPORTE DE CALIDAD - INTERNO"
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Información básica
        story.append(Paragraph("INFORMACIÓN BÁSICA", self.styles['CustomSubtitle']))
        
        basic_info = [
            ['Título:', report_data.get('title', '')],
            ['Tipo de Reporte:', 'Para Cliente' if report_type == 'cliente' else 'Interno'],
            ['Fecha:', datetime.now().strftime('%d/%m/%Y')]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 4*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#faf5ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Resumen ejecutivo
        if report_data.get('executive_summary'):
            story.append(Paragraph("RESUMEN EJECUTIVO", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('executive_summary', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Descripción del problema
        if report_data.get('problem_description'):
            story.append(Paragraph("DESCRIPCIÓN DEL PROBLEMA", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('problem_description', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Análisis de causa raíz
        if report_data.get('root_cause_analysis'):
            story.append(Paragraph("ANÁLISIS DE CAUSA RAÍZ", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('root_cause_analysis', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Acciones correctivas
        if report_data.get('corrective_actions'):
            story.append(Paragraph("ACCIONES CORRECTIVAS", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('corrective_actions', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Medidas preventivas
        if report_data.get('preventive_measures'):
            story.append(Paragraph("MEDIDAS PREVENTIVAS", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('preventive_measures', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Recomendaciones
        if report_data.get('recommendations'):
            story.append(Paragraph("RECOMENDACIONES", self.styles['CustomSubtitle']))
            story.append(Paragraph(report_data.get('recommendations', ''), self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Imágenes (si las hay)
        if images:
            story.append(PageBreak())
            story.append(Paragraph("IMÁGENES DEL REPORTE", self.styles['CustomSubtitle']))
            
            for i, image_data in enumerate(images):
                try:
                    story.append(Paragraph(f"Imagen {i+1}", self.styles['CustomBody']))
                    story.append(Spacer(1, 10))
                except Exception as e:
                    logger.error(f"Error procesando imagen {i+1}: {str(e)}")
        
        # Construir PDF
        doc.build(story, onFirstPage=self.add_header, onLaterPages=self.add_header)
        
        buffer.seek(0)
        return buffer.getvalue()
