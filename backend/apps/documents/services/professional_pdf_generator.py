#!/usr/bin/env python
"""
GENERADOR DE PDF PROFESIONAL - POLIFUSIÓN S.A.
Sistema de generación de PDFs con diseño corporativo verdaderamente profesional
"""

import io
import os
import base64
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, String
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.conf import settings
import logging
import os
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

# COLORES CORPORATIVOS DE POLIFUSIÓN
PRIMARY_BLUE = HexColor('#126FCC')      # Azul principal de Polifusión
SECONDARY_BLUE = HexColor('#1C3664')    # Azul secundario
ACCENT_GREEN = HexColor('#10B981')      # Verde éxito
WARNING_ORANGE = HexColor('#F59E0B')    # Naranja advertencia
LIGHT_GRAY = HexColor('#F8FAFC')       # Gris claro
MEDIUM_GRAY = HexColor('#E2E8F0')      # Gris medio
DARK_GRAY = HexColor('#64748B')        # Gris oscuro
TEXT_COLOR = HexColor('#1E293B')       # Color de texto principal
WHITE = HexColor('#FFFFFF')            # Blanco

class ProfessionalPDFGenerator:
    """
    Generador de PDFs verdaderamente profesional para Polifusión S.A.
    """
    
    def __init__(self):
        self.company_info = {
            'name': 'POLIFUSIÓN S.A.',
            'address': 'Lampa, Región Metropolitana',
            'location': 'Cacique Colin 2525',
            'phone': '(2) 2387 5000',
            'email': 'info@polifusion.cl'
        }
        
        # Configurar carpeta compartida
        self.shared_folder = getattr(settings, 'SHARED_FOLDER_PATH', 'Y:\\CONTROL DE CALIDAD\\postventa')
        
        # Crear estilos profesionales
        self.styles = getSampleStyleSheet()
        self._create_professional_styles()
    
    def _create_professional_styles(self):
        """Crear estilos profesionales para el PDF"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            fontName='Helvetica-Bold',
            textColor=PRIMARY_BLUE,
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            fontName='Helvetica-Bold',
            textColor=SECONDARY_BLUE,
            alignment=TA_CENTER,
            spaceAfter=15,
            spaceBefore=10
        ))
        
        # Título de sección
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=PRIMARY_BLUE,
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=15,
            borderWidth=0,
            borderColor=PRIMARY_BLUE,
            borderPadding=5,
            backColor=LIGHT_GRAY
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica',
            textColor=TEXT_COLOR,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            spaceBefore=3
        ))
        
        # Texto pequeño
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            textColor=DARK_GRAY,
            alignment=TA_LEFT,
            spaceAfter=3,
            spaceBefore=2
        ))
        
        # Texto de encabezado de tabla
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=WHITE,
            alignment=TA_CENTER,
            backColor=PRIMARY_BLUE
        ))
        
        # Texto de celda de tabla
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            textColor=TEXT_COLOR,
            alignment=TA_LEFT,
            leftIndent=5,
            rightIndent=5
        ))
    
    def create_logo_drawing(self):
        """Crear el logo real de Polifusión usando el archivo de imagen"""
        try:
            # Buscar el logo en diferentes formatos
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
            logo_paths = [
                os.path.join(assets_dir, 'logo_polifusion.png'),
                os.path.join(assets_dir, 'logo_polifusion.jpg'),
                os.path.join(assets_dir, 'logo_polifusion.jpeg'),
                os.path.join(assets_dir, 'Logo Polifusion.svg'),
                r"C:\Users\Jesus Diaz\Downloads\Logo Polifusion.svg"
            ]
            
            logo_path = None
            # Verificar que el archivo PNG no sea realmente un SVG
            for path in logo_paths:
                if os.path.exists(path):
                    if not path.endswith('.svg'):
                        # Verificar si es realmente un PNG
                        try:
                            with open(path, 'rb') as f:
                                header = f.read(8)
                                if header.startswith(b'\x89PNG'):
                                    logo_path = path
                                    break
                        except:
                            continue
                    else:
                        # Para SVG, usar directamente
                        logo_path = path
                        break
            
            if logo_path:
                logger.info(f"Usando logo real: {logo_path}")
                # Usar el logo real como imagen
                if logo_path.endswith('.svg'):
                    # Para SVG, crear un logo temporal por ahora
                    logger.warning("SVG no soportado directamente, usando logo temporal")
                    drawing = Drawing(200, 60)
                    drawing.add(Rect(0, 0, 200, 60, fillColor=PRIMARY_BLUE, strokeColor=PRIMARY_BLUE))
                    drawing.add(String(10, 30, "POLIFUSIÓN S.A.", 
                                      fontName='Helvetica-Bold', 
                                      fontSize=16, 
                                      fillColor=WHITE))
                    return drawing
                else:
                    # Para PNG/JPG, devolver la ruta para usar en create_header
                    return logo_path
            else:
                # Si no existe el logo, crear uno simple temporal
                logger.warning("Logo de Polifusión no encontrado en ninguna ubicación")
                logger.warning("Coloca tu logo en: backend/apps/documents/assets/logo_polifusion.png")
                drawing = Drawing(200, 60)
                drawing.add(Rect(0, 0, 200, 60, fillColor=PRIMARY_BLUE, strokeColor=PRIMARY_BLUE))
                drawing.add(String(10, 30, "POLIFUSIÓN S.A.", 
                                  fontName='Helvetica-Bold', 
                                  fontSize=16, 
                                  fillColor=WHITE))
                return drawing
                
        except Exception as e:
            logger.error(f"Error cargando logo: {str(e)}")
            # Logo de respaldo
            drawing = Drawing(200, 60)
            drawing.add(Rect(0, 0, 200, 60, fillColor=PRIMARY_BLUE, strokeColor=PRIMARY_BLUE))
            drawing.add(String(10, 30, "POLIFUSIÓN S.A.", 
                              fontName='Helvetica-Bold', 
                              fontSize=16, 
                              fillColor=WHITE))
            return drawing
    
    def create_header(self, canvas, doc):
        """Crear encabezado profesional y moderno"""
        canvas.saveState()
        
        # Fondo del encabezado más pequeño
        canvas.setFillColor(PRIMARY_BLUE)
        canvas.rect(0, A4[1] - 80, A4[0], 80, fill=1, stroke=0)
        
        # Logo profesional
        logo = self.create_logo_drawing()
        if isinstance(logo, str):  # Es una ruta de archivo PNG
            # Cargar imagen desde archivo
            from reportlab.platypus import Image as RLImage
            logo_image = RLImage(logo, width=150, height=45)
            logo_image.drawOn(canvas, 50, A4[1] - 65)
        elif hasattr(logo, 'drawOn'):  # Es un Drawing
            renderPDF.draw(logo, canvas, 50, A4[1] - 65)
        else:  # Es una Image
            logo.drawOn(canvas, 50, A4[1] - 65)
        
        # Información de la empresa alineada con el margen derecho
        canvas.setFillColor(WHITE)
        canvas.setFont('Helvetica', 9)
        # Calcular posición para alineación derecha
        text_width = len(self.company_info['address']) * 5  # Aproximación
        x_pos = A4[0] - 50 - text_width
        canvas.drawString(x_pos, A4[1] - 25, self.company_info['address'])
        
        text_width = len(self.company_info['location']) * 5
        x_pos = A4[0] - 50 - text_width
        canvas.drawString(x_pos, A4[1] - 35, self.company_info['location'])
        
        text_width = len(f"Tel: {self.company_info['phone']}") * 5
        x_pos = A4[0] - 50 - text_width
        canvas.drawString(x_pos, A4[1] - 45, f"Tel: {self.company_info['phone']}")
        
        # Línea decorativa moderna
        canvas.setStrokeColor(ACCENT_GREEN)
        canvas.setLineWidth(2)
        canvas.line(50, A4[1] - 85, A4[0] - 50, A4[1] - 85)
        
        canvas.restoreState()
    
    def create_footer(self, canvas, doc):
        """Crear pie de página profesional y moderno"""
        canvas.saveState()
        
        # Fondo del pie más pequeño
        canvas.setFillColor(LIGHT_GRAY)
        canvas.rect(0, 0, A4[0], 40, fill=1, stroke=0)
        
        # Línea decorativa superior
        canvas.setStrokeColor(PRIMARY_BLUE)
        canvas.setLineWidth(2)
        canvas.line(50, 40, A4[0] - 50, 40)
        
        # Información del pie
        canvas.setFillColor(DARK_GRAY)
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(50, 20, f"Página {doc.page}")
        
        canvas.setFont('Helvetica', 7)
        canvas.drawString(50, 10, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawString(A4[0] - 150, 10, "Polifusión S.A. - Control de Calidad")
        
        canvas.restoreState()
    
    def create_professional_table(self, data, headers, title=None):
        """Crear tabla profesional"""
        elements = []
        
        if title:
            elements.append(Paragraph(title, self.styles['SectionTitle']))
            elements.append(Spacer(1, 10))
        
        # Crear tabla
        table_data = [headers] + data
        
        # Calcular ancho de columnas
        num_cols = len(headers)
        col_widths = [A4[0] / num_cols] * num_cols
        
        table = Table(table_data, colWidths=col_widths)
        
        # Estilo de tabla profesional
        table_style = [
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Filas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, MEDIUM_GRAY),
            ('LINEBELOW', (0, 0), (-1, 0), 2, PRIMARY_BLUE),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        table.setStyle(TableStyle(table_style))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _save_to_shared_folder(self, local_path, incident_id, document_type, filename, lab_type=None):
        """
        Guardar el PDF en la carpeta compartida de red
        Para reportes de laboratorio, separar entre cliente e internos
        """
        try:
            # Determinar la carpeta según el tipo de documento
            if document_type == 'lab-reports' and lab_type:
                # Para reportes de laboratorio, usar subcarpetas específicas
                folder_name = f'lab-reports-{lab_type}'  # lab-reports-cliente o lab-reports-interno
            else:
                folder_name = document_type
            
            # Crear estructura de carpetas en la carpeta compartida
            incident_folder = os.path.join(self.shared_folder, 'documents', folder_name, f'incident_{incident_id}')
            os.makedirs(incident_folder, exist_ok=True)
            
            # Ruta de destino en la carpeta compartida
            shared_path = os.path.join(incident_folder, filename)
            
            # Copiar archivo a la carpeta compartida
            shutil.copy2(local_path, shared_path)
            
            logger.info(f"PDF guardado en carpeta compartida: {shared_path}")
            return shared_path
            
        except Exception as e:
            logger.error(f"Error guardando en carpeta compartida: {str(e)}")
            return None
    
    def generate_visit_report_pdf(self, report_data, output_path):
        """Generar PDF de reporte de visita profesional y moderno"""
        try:
            # Crear documento con márgenes optimizados
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=140,
                bottomMargin=80
            )
            
            # Elementos del documento
            story = []
            
            # Título principal con diseño moderno
            story.append(Paragraph("REPORTE DE VISITA TÉCNICA", self.styles['MainTitle']))
            story.append(Spacer(1, 25))
            
            # Información del reporte en diseño de dos columnas
            left_info = [
                ['Número de Orden:', report_data.get('order_number', 'N/A')],
                ['Fecha de Visita:', report_data.get('visit_date', 'N/A')],
                ['Cliente:', report_data.get('client', 'N/A')],
                ['Proyecto:', report_data.get('project', 'N/A')]
            ]
            
            right_info = [
                ['Dirección:', report_data.get('address', 'N/A')],
                ['Técnico:', report_data.get('technician', 'N/A')],
                ['Vendedor:', report_data.get('salesperson', 'N/A')],
                ['Estado:', report_data.get('status', 'En Proceso')]
            ]
            
            # INFORMACIÓN DEL REPORTE - Diseño profesional organizado
            story.append(Paragraph("INFORMACIÓN DEL REPORTE", self.styles['SectionTitle']))
            story.append(Spacer(1, 10))
            
            # Sección 1: Datos de la Orden
            order_data = [
                ['Número de Orden:', report_data.get('order_number', 'N/A')],
                ['Fecha de Visita:', report_data.get('visit_date', 'N/A')],
                ['Estado:', report_data.get('status', 'En Proceso')]
            ]
            
            order_table = Table(order_data, colWidths=[120, 300])
            order_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
                ('GRID', (0, 0), (-1, -1), 1, MEDIUM_GRAY),
            ]))
            
            story.append(order_table)
            story.append(Spacer(1, 10))
            
            # Sección 2: Datos del Cliente y Proyecto
            client_data = [
                ['Cliente:', report_data.get('client_name', report_data.get('client', 'N/A'))],
                ['Proyecto:', report_data.get('project_name', report_data.get('project', 'N/A'))],
                ['Dirección:', report_data.get('address', 'N/A')]
            ]
            
            client_table = Table(client_data, colWidths=[120, 300])
            client_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
                ('GRID', (0, 0), (-1, -1), 1, MEDIUM_GRAY),
            ]))
            
            story.append(client_table)
            story.append(Spacer(1, 10))
            
            # Sección 3: Personal Responsable
            staff_data = [
                ['Técnico Responsable:', report_data.get('technician', 'N/A')],
                ['Vendedor:', report_data.get('salesperson', 'N/A')]
            ]
            
            staff_table = Table(staff_data, colWidths=[120, 300])
            staff_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
                ('GRID', (0, 0), (-1, -1), 1, MEDIUM_GRAY),
            ]))
            
            story.append(staff_table)
            story.append(Spacer(1, 15))
            
            # MOTIVO DE LA VISITA - Diseño profesional
            if report_data.get('visit_reason'):
                story.append(Paragraph("MOTIVO DE LA VISITA", self.styles['SectionTitle']))
                story.append(Spacer(1, 8))
                
                # Crear caja profesional para el motivo
                reason_style = ParagraphStyle(
                    'ReasonBox',
                    parent=self.styles['NormalText'],
                    fontSize=11,
                    fontName='Helvetica',
                    textColor=TEXT_COLOR,
                    alignment=TA_LEFT,
                    spaceAfter=6,
                    spaceBefore=3,
                    backColor=WHITE,
                    borderWidth=2,
                    borderColor=PRIMARY_BLUE,
                    borderPadding=12,
                    leftIndent=10,
                    rightIndent=10
                )
                
                story.append(Paragraph(report_data['visit_reason'], reason_style))
                story.append(Spacer(1, 15))
            
            # OBSERVACIONES GENERALES - Diseño profesional
            if report_data.get('general_observations'):
                story.append(Paragraph("OBSERVACIONES GENERALES", self.styles['SectionTitle']))
                story.append(Spacer(1, 8))
                
                # Crear caja profesional para las observaciones
                obs_style = ParagraphStyle(
                    'ObservationsBox',
                    parent=self.styles['NormalText'],
                    fontSize=11,
                    fontName='Helvetica',
                    textColor=TEXT_COLOR,
                    alignment=TA_LEFT,
                    spaceAfter=6,
                    spaceBefore=3,
                    backColor=WHITE,
                    borderWidth=2,
                    borderColor=ACCENT_GREEN,
                    borderPadding=12,
                    leftIndent=10,
                    rightIndent=10
                )
                
                story.append(Paragraph(report_data['general_observations'], obs_style))
                story.append(Spacer(1, 15))
            
            # Información de la incidencia relacionada
            if 'incident' in report_data:
                incident = report_data['incident']
                incident_info = [
                    ['Código de Incidencia:', incident.get('code', 'N/A')],
                    ['Descripción:', incident.get('descripcion', 'N/A')],
                    ['Prioridad:', incident.get('prioridad', 'N/A')],
                    ['Estado:', incident.get('estado', 'N/A')],
                    ['Proveedor:', incident.get('provider', 'N/A')],
                    ['SKU:', incident.get('sku', 'N/A')],
                    ['Lote:', incident.get('lote', 'N/A')]
                ]
                
                story.extend(self.create_professional_table(
                    incident_info,
                    ['Campo', 'Información'],
                    'INFORMACIÓN DE LA INCIDENCIA'
                ))
            
            # Sección de firmas profesional
            story.append(Spacer(1, 20))
            story.append(Paragraph("FIRMAS Y APROBACIONES", self.styles['SectionTitle']))
            story.append(Spacer(1, 10))
            
            # Tabla de firmas simplificada - solo 2 líneas
            signature_data = [
                ['FIRMA TÉCNICO', 'FIRMA INSTALADOR'],
                ['', ''],
                ['Nombre: _________________________', 'Nombre: _________________________'],
                ['', ''],
                ['Firma: _________________________', 'Firma: _________________________']
            ]
            
            signature_table = Table(signature_data, colWidths=[A4[0]/2 - 40, A4[0]/2 - 40])
            signature_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 12),
                ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 2), (-1, -1), 10),
                ('LINEBELOW', (0, 2), (0, 2), 1, DARK_GRAY),
                ('LINEBELOW', (1, 2), (1, 2), 1, DARK_GRAY),
                ('LINEBELOW', (0, 4), (0, 4), 1, DARK_GRAY),
                ('LINEBELOW', (1, 4), (1, 4), 1, DARK_GRAY),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(signature_table)
            
            # Construir PDF con encabezado y pie de página
            doc.build(story, onFirstPage=self.create_header, onLaterPages=self.create_header)
            
            # Guardar en carpeta compartida si se proporciona incident_id
            if 'incident' in report_data and 'id' in report_data['incident']:
                incident_id = report_data['incident']['id']
                filename = os.path.basename(output_path)
                shared_path = self._save_to_shared_folder(output_path, incident_id, 'visit-reports', filename)
                if shared_path:
                    logger.info(f"PDF guardado en carpeta compartida: {shared_path}")
            
            logger.info(f"PDF profesional generado exitosamente: {output_path}")
            
            # Leer el contenido del archivo generado
            with open(output_path, 'rb') as f:
                pdf_content = f.read()
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generando PDF profesional: {str(e)}")
            return False
    
    def generate_lab_report_client_pdf(self, report_data, output_path):
        """Generar PDF de reporte de laboratorio para cliente"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=120,
                bottomMargin=70
            )
            
            story = []
            
            # Título principal
            story.append(Paragraph("REPORTE DE LABORATORIO - CLIENTE", self.styles['MainTitle']))
            story.append(Spacer(1, 20))
            
            # Información del reporte
            report_info = [
                ['Cliente:', report_data.get('client', 'N/A')],
                ['Proyecto:', report_data.get('project', 'N/A')],
                ['Descripción:', report_data.get('description', 'N/A')],
                ['Antecedentes:', report_data.get('project_background', 'N/A')],
                ['Pruebas Realizadas:', report_data.get('tests_performed', 'N/A')],
                ['Resultados:', report_data.get('results', 'N/A')],
                ['Conclusiones:', report_data.get('conclusions', 'N/A')],
                ['Recomendaciones:', report_data.get('recommendations', 'N/A')],
                ['Experto Técnico:', report_data.get('technical_expert_name', 'N/A')]
            ]
            
            story.extend(self.create_professional_table(
                report_info,
                ['Campo', 'Información'],
                'INFORMACIÓN DEL REPORTE'
            ))
            
            # Construir PDF
            doc.build(story, onFirstPage=self.create_header, onLaterPages=self.create_header)
            
            # Guardar en carpeta compartida si se proporciona incident_id
            if 'incident_id' in report_data:
                incident_id = report_data['incident_id']
                filename = os.path.basename(output_path)
                shared_path = self._save_to_shared_folder(output_path, incident_id, 'lab-reports', filename, 'cliente')
                if shared_path:
                    logger.info(f"PDF guardado en carpeta compartida: {shared_path}")
            
            logger.info(f"PDF de laboratorio para cliente generado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando PDF de laboratorio para cliente: {str(e)}")
            return False
    
    def generate_lab_report_internal_pdf(self, report_data, output_path):
        """Generar PDF de reporte de laboratorio interno"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=120,
                bottomMargin=70
            )
            
            story = []
            
            # Título principal
            story.append(Paragraph("REPORTE DE LABORATORIO - INTERNO", self.styles['MainTitle']))
            story.append(Spacer(1, 20))
            
            # Información del reporte
            report_info = [
                ['Proyecto Interno:', report_data.get('internal_project', 'N/A')],
                ['Responsable:', report_data.get('responsible', 'N/A')],
                ['Descripción:', report_data.get('description', 'N/A')],
                ['Objetivo:', report_data.get('objective', 'N/A')],
                ['Metodología:', report_data.get('methodology', 'N/A')],
                ['Pruebas Realizadas:', report_data.get('tests_performed', 'N/A')],
                ['Resultados:', report_data.get('results', 'N/A')],
                ['Análisis Interno:', report_data.get('internal_analysis', 'N/A')],
                ['Conclusiones:', report_data.get('conclusions', 'N/A')],
                ['Acciones Correctivas:', report_data.get('corrective_actions', 'N/A')],
                ['Técnico Responsable:', report_data.get('technical_expert_name', 'N/A')]
            ]
            
            story.extend(self.create_professional_table(
                report_info,
                ['Campo', 'Información'],
                'INFORMACIÓN DEL REPORTE INTERNO'
            ))
            
            # Construir PDF
            doc.build(story, onFirstPage=self.create_header, onLaterPages=self.create_header)
            
            # Guardar en carpeta compartida si se proporciona incident_id
            if 'incident_id' in report_data:
                incident_id = report_data['incident_id']
                filename = os.path.basename(output_path)
                shared_path = self._save_to_shared_folder(output_path, incident_id, 'lab-reports', filename, 'interno')
                if shared_path:
                    logger.info(f"PDF guardado en carpeta compartida: {shared_path}")
            
            logger.info(f"PDF de laboratorio interno generado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando PDF de laboratorio interno: {str(e)}")
            return False
    
    def generate_supplier_report_pdf(self, report_data, output_path):
        """Generar PDF de reporte de proveedor profesional"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=120,
                bottomMargin=70
            )
            
            story = []
            
            # Título principal
            story.append(Paragraph("REPORTE PARA PROVEEDOR", self.styles['MainTitle']))
            story.append(Spacer(1, 20))
            
            # Información del proveedor
            supplier_info = [
                ['Proveedor:', report_data.get('supplier_name', 'N/A')],
                ['Contacto:', report_data.get('supplier_contact', 'N/A')],
                ['Email:', report_data.get('supplier_email', 'N/A')],
                ['Asunto:', report_data.get('subject', 'N/A')]
            ]
            
            story.extend(self.create_professional_table(
                supplier_info,
                ['Campo', 'Información'],
                'INFORMACIÓN DEL PROVEEDOR'
            ))
            
            # Contenido del reporte
            if report_data.get('introduction'):
                story.append(Paragraph("INTRODUCCIÓN", self.styles['SectionTitle']))
                story.append(Paragraph(report_data['introduction'], self.styles['NormalText']))
                story.append(Spacer(1, 15))
            
            if report_data.get('problem_description'):
                story.append(Paragraph("DESCRIPCIÓN DEL PROBLEMA", self.styles['SectionTitle']))
                story.append(Paragraph(report_data['problem_description'], self.styles['NormalText']))
                story.append(Spacer(1, 15))
            
            if report_data.get('technical_analysis'):
                story.append(Paragraph("ANÁLISIS TÉCNICO", self.styles['SectionTitle']))
                story.append(Paragraph(report_data['technical_analysis'], self.styles['NormalText']))
                story.append(Spacer(1, 15))
            
            if report_data.get('recommendations'):
                story.append(Paragraph("RECOMENDACIONES", self.styles['SectionTitle']))
                story.append(Paragraph(report_data['recommendations'], self.styles['NormalText']))
                story.append(Spacer(1, 15))
            
            if report_data.get('expected_improvements'):
                story.append(Paragraph("MEJORAS ESPERADAS", self.styles['SectionTitle']))
                story.append(Paragraph(report_data['expected_improvements'], self.styles['NormalText']))
                story.append(Spacer(1, 15))
            
            # Construir PDF
            doc.build(story, onFirstPage=self.create_header, onLaterPages=self.create_header)
            
            # Guardar en carpeta compartida si se proporciona incident_id
            if 'incident_id' in report_data:
                incident_id = report_data['incident_id']
                filename = os.path.basename(output_path)
                shared_path = self._save_to_shared_folder(output_path, incident_id, 'supplier-reports', filename)
                if shared_path:
                    logger.info(f"PDF guardado en carpeta compartida: {shared_path}")
            
            logger.info(f"PDF de proveedor profesional generado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando PDF de proveedor: {str(e)}")
            return False
    
    def generate_quality_report_pdf(self, report_data, output_path):
        """Generar PDF de reporte de calidad profesional"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=120,
                bottomMargin=70
            )
            
            story = []
            
            # Título principal
            story.append(Paragraph("REPORTE DE CALIDAD", self.styles['MainTitle']))
            story.append(Spacer(1, 20))
            
            # Información del reporte
            quality_info = [
                ['Número de Reporte:', report_data.get('report_number', 'N/A')],
                ['Fecha:', report_data.get('date', 'N/A')],
                ['Cliente:', report_data.get('client', 'N/A')],
                ['Producto:', report_data.get('product', 'N/A')],
                ['Lote:', report_data.get('batch', 'N/A')],
                ['Inspector:', report_data.get('inspector', 'N/A')]
            ]
            
            story.extend(self.create_professional_table(
                quality_info,
                ['Campo', 'Información'],
                'INFORMACIÓN DEL REPORTE'
            ))
            
            # Construir PDF
            doc.build(story, onFirstPage=self.create_header, onLaterPages=self.create_header)
            
            # Guardar en carpeta compartida si se proporciona incident_id
            if 'incident_id' in report_data:
                incident_id = report_data['incident_id']
                filename = os.path.basename(output_path)
                shared_path = self._save_to_shared_folder(output_path, incident_id, 'quality-reports', filename)
                if shared_path:
                    logger.info(f"PDF guardado en carpeta compartida: {shared_path}")
            
            logger.info(f"PDF de calidad profesional generado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando PDF de calidad: {str(e)}")
            return False