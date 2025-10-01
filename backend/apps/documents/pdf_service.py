"""
PDF Service for generating and editing PDF documents
"""

import os
import io
from typing import Dict, Any, Optional
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from apps.documents.models import Document
from apps.users.models import User

# Try to import reportlab, if not available, use fallback
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not available. PDF generation will be disabled.")

import logging

logger = logging.getLogger(__name__)

class PDFDocumentService:
    """Service for generating and editing PDF documents"""
    
    def __init__(self):
        self.shared_folder = getattr(settings, 'SHARED_DOCUMENTS_PATH', 'Y:\\CONTROL DE CALIDAD\\postventa')
        self.documents_path = os.path.join(self.shared_folder, 'documents')
        self.templates_path = os.path.join(self.shared_folder, 'templates')
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _get_incident_folder_path(self, incident_code=None):
        """Get or create folder path for incident documents"""
        if incident_code:
            # Create incident-specific folder
            incident_folder = os.path.join(self.documents_path, f"INC_{incident_code}")
            os.makedirs(incident_folder, exist_ok=True)
            return incident_folder
        else:
            # Use general documents folder
            return self.documents_path
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [self.documents_path, self.templates_path]
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")
    
    def _get_logo_path(self) -> Optional[str]:
        """Get the path to the company logo"""
        logo_paths = [
            os.path.join(self.shared_folder, 'images', 'logo.png'),
            os.path.join(self.shared_folder, 'images', 'logo.jpg'),
            os.path.join(self.shared_folder, 'images', 'polifusion_logo.png'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png'),
        ]
        
        for path in logo_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _create_header_footer(self, canvas, doc):
        """Create header and footer for PDF documents"""
        if not REPORTLAB_AVAILABLE:
            return
        
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.HexColor('#2563eb'))  # Blue color
        
        # Company name
        canvas.drawString(50, 750, "POLIFUSION LAB")
        
        # Logo (if available)
        logo_path = self._get_logo_path()
        if logo_path:
            try:
                logo = ImageReader(logo_path)
                canvas.drawImage(logo, 450, 720, width=100, height=30, preserveAspectRatio=True)
            except Exception as e:
                logger.warning(f"Could not add logo to PDF: {e}")
        
        # Line separator
        canvas.setStrokeColor(colors.HexColor('#2563eb'))
        canvas.setLineWidth(2)
        canvas.line(50, 710, 550, 710)
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(50, 50, "Sistema de Gestión de Calidad - Polifusión Lab")
        canvas.drawString(450, 50, f"Página {doc.page}")
        
        # Footer line
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(1)
        canvas.line(50, 60, 550, 60)
        
        # Restore the state
        canvas.restoreState()
    
    def _create_styles(self):
        """Create custom styles for PDF documents"""
        if not REPORTLAB_AVAILABLE:
            return {}
        
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2563eb'),
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        )
        
        # Table header style
        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER
        )
        
        return {
            'title': title_style,
            'subtitle': subtitle_style,
            'normal': normal_style,
            'table_header': table_header_style
        }
    
    def _save_document_metadata(self, data: Dict[str, Any], filename: str, filepath: str, document_type: str):
        """Save document metadata to database"""
        try:
            # Get or create system user
            user, created = User.objects.get_or_create(
                username='system',
                defaults={
                    'email': 'system@polifusion.cl',
                    'first_name': 'Sistema',
                    'last_name': 'Polifusión',
                    'role': 'admin'
                }
            )
            
            # Create document record
            Document.objects.create(
                title=data.get('title', filename),
                document_type=document_type,
                content_html=f"<p>Documento generado: {filename}</p>",
                pdf_path=filepath,
                is_final=True,
                created_by=user,
                notes=f"Archivo guardado en: {filepath}"
            )
            
            logger.info(f"Document metadata saved to database: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving document metadata: {e}")
    
    def generate_polifusion_lab_report_pdf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Polifusión lab report as PDF"""
        if not REPORTLAB_AVAILABLE:
            return {
                'success': False,
                'error': 'ReportLab no está disponible. No se puede generar PDF.',
                'pdf_path': None,
                'filename': None
            }
        
        try:
            # Get incident code if provided
            incident_code = data.get('incident_code')
            
            # Create filename
            filename = f"Informe_Laboratorio_{data.get('cliente', 'Cliente')}_{data.get('proyecto', 'Proyecto')}_{data.get('fecha_solicitud', '')}.pdf"
            
            # Get appropriate folder path
            folder_path = self._get_incident_folder_path(incident_code)
            file_path = os.path.join(folder_path, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=100,
                bottomMargin=100
            )
            
            # Create styles
            styles = self._create_styles()
            
            # Build content
            story = []
            
            # Title
            story.append(Paragraph("INFORME DE LABORATORIO", styles['title']))
            story.append(Spacer(1, 20))
            
            # Client information
            story.append(Paragraph("INFORMACIÓN DEL CLIENTE", styles['subtitle']))
            client_data = [
                ['Cliente:', data.get('cliente', 'No especificado')],
                ['Proyecto:', data.get('proyecto', 'No especificado')],
                ['Ubicación:', data.get('ubicacion', 'No especificado')],
                ['Fecha de Solicitud:', data.get('fecha_solicitud', 'No especificado')],
                ['Solicitante:', data.get('solicitante', 'No especificado')],
            ]
            
            client_table = Table(client_data, colWidths=[2*inch, 4*inch])
            client_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]))
            story.append(client_table)
            story.append(Spacer(1, 20))
            
            # Technical information
            story.append(Paragraph("INFORMACIÓN TÉCNICA", styles['subtitle']))
            tech_data = [
                ['Diámetro:', data.get('diametro', 'No especificado')],
                ['Presión:', data.get('presion', 'No especificado')],
                ['Temperatura:', data.get('temperatura', 'No especificado')],
                ['Informante:', data.get('informante', 'No especificado')],
            ]
            
            tech_table = Table(tech_data, colWidths=[2*inch, 4*inch])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]))
            story.append(tech_table)
            story.append(Spacer(1, 20))
            
            # Additional tests
            if data.get('ensayos_adicionales'):
                story.append(Paragraph("ENSAYOS ADICIONALES", styles['subtitle']))
                story.append(Paragraph(data.get('ensayos_adicionales', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Detailed comments
            if data.get('comentarios_detallados'):
                story.append(Paragraph("COMENTARIOS DETALLADOS", styles['subtitle']))
                story.append(Paragraph(data.get('comentarios_detallados', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Conclusions
            if data.get('conclusiones_detalladas'):
                story.append(Paragraph("CONCLUSIONES", styles['subtitle']))
                story.append(Paragraph(data.get('conclusiones_detalladas', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Expert signature
            story.append(Paragraph("RESPONSABLE TÉCNICO", styles['subtitle']))
            expert_data = [
                ['Nombre:', data.get('experto_nombre', 'No especificado')],
                ['Fecha:', data.get('fecha_solicitud', 'No especificado')],
            ]
            
            expert_table = Table(expert_data, colWidths=[2*inch, 4*inch])
            expert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            story.append(expert_table)
            
            # Build PDF
            doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'file_type': 'pdf'
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF lab report: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_type': 'pdf'
            }
    
    def generate_polifusion_incident_report_pdf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Polifusión incident report as PDF"""
        if not REPORTLAB_AVAILABLE:
            return {
                'success': False,
                'error': 'ReportLab no está disponible. No se puede generar PDF.',
                'pdf_path': None,
                'filename': None
            }
        
        try:
            # Create filename
            filename = f"Informe_Incidencia_{data.get('cliente', 'Cliente')}_{data.get('obra', 'Obra')}_{data.get('fecha_deteccion', '')}.pdf"
            file_path = os.path.join(self.documents_path, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=100,
                bottomMargin=100
            )
            
            # Create styles
            styles = self._create_styles()
            
            # Build content
            story = []
            
            # Title
            story.append(Paragraph("INFORME DE INCIDENCIA", styles['title']))
            story.append(Spacer(1, 20))
            
            # Incident information
            story.append(Paragraph("INFORMACIÓN DE LA INCIDENCIA", styles['subtitle']))
            incident_data = [
                ['Proveedor:', data.get('proveedor', 'No especificado')],
                ['Obra:', data.get('obra', 'No especificado')],
                ['Cliente:', data.get('cliente', 'No especificado')],
                ['Fecha de Detección:', data.get('fecha_deteccion', 'No especificado')],
            ]
            
            incident_table = Table(incident_data, colWidths=[2*inch, 4*inch])
            incident_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]))
            story.append(incident_table)
            story.append(Spacer(1, 20))
            
            # Problem description
            if data.get('descripcion_problema'):
                story.append(Paragraph("DESCRIPCIÓN DEL PROBLEMA", styles['subtitle']))
                story.append(Paragraph(data.get('descripcion_problema', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Immediate actions
            if data.get('acciones_inmediatas'):
                story.append(Paragraph("ACCIONES INMEDIATAS", styles['subtitle']))
                story.append(Paragraph(data.get('acciones_inmediatas', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Action evolution
            if data.get('evolucion_acciones'):
                story.append(Paragraph("EVOLUCIÓN DE ACCIONES", styles['subtitle']))
                story.append(Paragraph(data.get('evolucion_acciones', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Observations
            if data.get('observaciones'):
                story.append(Paragraph("OBSERVACIONES", styles['subtitle']))
                story.append(Paragraph(data.get('observaciones', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'file_type': 'pdf'
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF incident report: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_type': 'pdf'
            }
    
    def generate_polifusion_visit_report_pdf(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Polifusión visit report as PDF"""
        if not REPORTLAB_AVAILABLE:
            return {
                'success': False,
                'error': 'ReportLab no está disponible. No se puede generar PDF.',
                'pdf_path': None,
                'filename': None
            }
        
        try:
            # Create filename
            filename = f"Reporte_Visita_{data.get('cliente', 'Cliente')}_{data.get('fecha_visita', '')}.pdf"
            file_path = os.path.join(self.documents_path, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=100,
                bottomMargin=100
            )
            
            # Create styles
            styles = self._create_styles()
            
            # Build content
            story = []
            
            # Title
            story.append(Paragraph("REPORTE DE VISITA TÉCNICA", styles['title']))
            story.append(Spacer(1, 20))
            
            # Visit information
            story.append(Paragraph("INFORMACIÓN DE LA VISITA", styles['subtitle']))
            visit_data = [
                ['Cliente:', data.get('cliente', 'No especificado')],
                ['Fecha de Visita:', data.get('fecha_visita', 'No especificado')],
                ['Técnico Responsable:', data.get('tecnico_responsable', 'No especificado')],
                ['Tipo de Visita:', data.get('tipo_visita', 'No especificado')],
            ]
            
            visit_table = Table(visit_data, colWidths=[2*inch, 4*inch])
            visit_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ]))
            story.append(visit_table)
            story.append(Spacer(1, 20))
            
            # Visit details
            if data.get('detalles_visita'):
                story.append(Paragraph("DETALLES DE LA VISITA", styles['subtitle']))
                story.append(Paragraph(data.get('detalles_visita', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Findings
            if data.get('hallazgos'):
                story.append(Paragraph("HALLAZGOS", styles['subtitle']))
                story.append(Paragraph(data.get('hallazgos', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Recommendations
            if data.get('recomendaciones'):
                story.append(Paragraph("RECOMENDACIONES", styles['subtitle']))
                story.append(Paragraph(data.get('recomendaciones', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Next steps
            if data.get('proximos_pasos'):
                story.append(Paragraph("PRÓXIMOS PASOS", styles['subtitle']))
                story.append(Paragraph(data.get('proximos_pasos', ''), styles['normal']))
                story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'file_type': 'pdf'
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF visit report: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_type': 'pdf'
            }
