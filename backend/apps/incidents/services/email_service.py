from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import logging
import os
import subprocess
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import win32com.client

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de correos automáticos usando Django"""
        
    def send_escalation_to_quality_email(self, incident, visit_report_path=None):
        """
        Crea un correo en Outlook usando COM automation
        """
        try:
            # Destinatarios
            to_emails = 'vlutz@polifusion.cl; cmunizaga@polifusion.cl'
            cc_emails = 'jdiaz@polifusion.cl; mmiranda@polifusion.cl; rcruz@polifusion.cl; pestay@polifusion.cl'
            
            # Asunto del correo
            subject = f'[ESCALAMIENTO A CALIDAD] {incident.code} - {incident.cliente}'
            
            # Generar contenido HTML
            html_content = self._generate_quality_escalation_body(incident)
            
            # Crear aplicación de Outlook
            outlook_app = win32com.client.Dispatch("Outlook.Application")
            mail_item = outlook_app.CreateItem(0)  # 0 = olMailItem
            
            # Configurar el correo
            mail_item.To = to_emails
            mail_item.CC = cc_emails
            mail_item.Subject = subject
            mail_item.HTMLBody = html_content
            
            # Adjuntar reporte de visita si existe
            if visit_report_path and os.path.exists(visit_report_path):
                mail_item.Attachments.Add(visit_report_path)
            
            # Mostrar el correo (no enviar automáticamente)
            mail_item.Display()
            
            logger.info(f"Correo de escalamiento creado en Outlook para incidencia {incident.code}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando correo en Outlook: {str(e)}")
            return False
    
    def send_escalation_to_supplier_email(self, incident, quality_report_path=None):
        """
        Crea un correo en Outlook para escalamiento a proveedor usando COM automation
        """
        try:
            # Destinatarios
            to_emails = 'vlutz@polifusion.cl; cmunizaga@polifusion.cl'
            cc_emails = 'jdiaz@polifusion.cl; mmiranda@polifusion.cl; rcruz@polifusion.cl; pestay@polifusion.cl'
            
            # Asunto del correo
            subject = f'[ESCALAMIENTO A PROVEEDOR] {incident.code} - {incident.cliente}'
            
            # Generar contenido HTML
            html_content = self._generate_supplier_escalation_body(incident)
            
            # Crear aplicación de Outlook
            outlook_app = win32com.client.Dispatch("Outlook.Application")
            mail_item = outlook_app.CreateItem(0)  # 0 = olMailItem
            
            # Configurar el correo
            mail_item.To = to_emails
            mail_item.CC = cc_emails
            mail_item.Subject = subject
            mail_item.HTMLBody = html_content
            
            # Adjuntar reporte de calidad si existe
            if quality_report_path and os.path.exists(quality_report_path):
                mail_item.Attachments.Add(quality_report_path)
            
            # Mostrar el correo (no enviar automáticamente)
            mail_item.Display()
            
            logger.info(f"Correo de escalamiento a proveedor creado en Outlook para incidencia {incident.code}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando correo de escalamiento a proveedor en Outlook: {str(e)}")
            return False
    
    def _generate_quality_escalation_body(self, incident):
        """Genera el cuerpo del correo de escalamiento a calidad"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-left: 4px solid #007bff; }}
                .content {{ padding: 20px; }}
                .incident-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ background-color: #e9ecef; padding: 15px; font-size: 12px; color: #6c757d; }}
                .highlight {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 ESCALAMIENTO A CALIDAD - INCIDENCIA {incident.code}</h2>
                <p><strong>Fecha:</strong> {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            
            <div class="content">
                <p>Estimado equipo de Calidad,</p>
                
                <p>Se ha escalado la siguiente incidencia para su análisis y evaluación:</p>
                
                <div class="incident-info">
                    <h3>📋 Información de la Incidencia</h3>
                    <p><strong>Código:</strong> {incident.code}</p>
                    <p><strong>Cliente:</strong> {incident.cliente}</p>
                    <p><strong>Proveedor:</strong> {incident.provider}</p>
                    <p><strong>Obra:</strong> {incident.obra}</p>
                    <p><strong>Categoría:</strong> {incident.categoria}</p>
                    <p><strong>Subcategoría:</strong> {incident.subcategoria or 'N/A'}</p>
                    <p><strong>Responsable Técnico:</strong> {incident.responsable}</p>
                    <p><strong>Prioridad:</strong> <span class="highlight">{incident.prioridad}</span></p>
                </div>
                
                <div class="incident-info">
                    <h3>📝 Descripción del Problema</h3>
                    <p>{incident.descripcion}</p>
                </div>
                
                
                <p><strong>📎 Adjunto:</strong> Reporte de Visita Técnica (PDF)</p>
                
                <p><strong>🎯 Próximos Pasos:</strong></p>
                <ul>
                    <li>Revisar el reporte de visita adjunto</li>
                    <li>Analizar las muestras del producto</li>
                    <li>Determinar si se requiere análisis de laboratorio</li>
                    <li>Evaluar si es necesario escalar al proveedor</li>
                </ul>
                
                <p>Por favor, mantengan informado al equipo técnico sobre el progreso del análisis.</p>
                
                <p>Saludos cordiales,<br>
                <strong>Equipo Técnico - Polifusion</strong></p>
            </div>
            
            <div class="footer">
                <p>Este es un correo automático del Sistema de Gestión de Incidencias Polifusion</p>
                <p>Para consultas, contactar a: jdiaz@polifusion.cl</p>
            </div>
        </body>
        </html>
        """
    
    def _generate_supplier_escalation_body(self, incident):
        """Genera el cuerpo del correo de escalamiento a proveedor"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-left: 4px solid #28a745; }}
                .content {{ padding: 20px; }}
                .incident-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ background-color: #e9ecef; padding: 15px; font-size: 12px; color: #6c757d; }}
                .highlight {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📤 ESCALAMIENTO A PROVEEDOR - INCIDENCIA {incident.code}</h2>
                <p><strong>Fecha:</strong> {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            
            <div class="content">
                <p>Estimado equipo,</p>
                
                <p>Se ha escalado la siguiente incidencia al proveedor para su revisión y respuesta:</p>
                
                <div class="incident-info">
                    <h3>📋 Información de la Incidencia</h3>
                    <p><strong>Código:</strong> {incident.code}</p>
                    <p><strong>Cliente:</strong> {incident.cliente}</p>
                    <p><strong>Proveedor:</strong> {incident.provider}</p>
                    <p><strong>Obra:</strong> {incident.obra}</p>
                    <p><strong>Categoría:</strong> {incident.categoria}</p>
                    <p><strong>Subcategoría:</strong> {incident.subcategoria or 'N/A'}</p>
                    <p><strong>Prioridad:</strong> <span class="highlight">{incident.prioridad}</span></p>
                </div>
                
                <div class="incident-info">
                    <h3>📝 Descripción del Problema</h3>
                    <p>{incident.descripcion}</p>
                </div>
                
                
                <p><strong>📎 Adjunto:</strong> Reporte de Calidad (PDF)</p>
                
                <p><strong>🎯 Próximos Pasos:</strong></p>
                <ul>
                    <li>Contactar al proveedor con la información adjunta</li>
                    <li>Solicitar análisis técnico del producto</li>
                    <li>Coordinar muestras para análisis de laboratorio si es necesario</li>
                    <li>Mantener seguimiento de la respuesta del proveedor</li>
                </ul>
                
                <p>Saludos cordiales,<br>
                <strong>Equipo de Calidad - Polifusion</strong></p>
            </div>
            
            <div class="footer">
                <p>Este es un correo automático del Sistema de Gestión de Incidencias Polifusion</p>
                <p>Para consultas, contactar a: jdiaz@polifusion.cl</p>
            </div>
        </body>
        </html>
        """
