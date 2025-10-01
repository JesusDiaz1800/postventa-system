"""
Gestor de archivos para el sistema de documentos
Maneja almacenamiento, organización y trazabilidad de documentos
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class FileManager:
    """
    Gestor de archivos para documentos
    """
    
    def __init__(self, base_path: str):
        """
        Inicializar gestor de archivos
        
        Args:
            base_path: Ruta base para almacenar documentos
        """
        self.base_path = base_path
        self.library_path = os.path.join(base_path, 'library')
        self.shared_path = os.path.join(base_path, 'shared')
        
        # Crear directorios necesarios
        self._create_directories()
        
        logger.info(f"FileManager inicializado en: {base_path}")
    
    def _create_directories(self):
        """Crear estructura de directorios necesaria"""
        directories = [
            self.library_path,
            self.shared_path,
            os.path.join(self.library_path, 'incidents'),
            os.path.join(self.library_path, 'visit_reports'),
            os.path.join(self.library_path, 'lab_reports'),
            os.path.join(self.library_path, 'supplier_reports'),
            os.path.join(self.shared_path, 'incidents'),
            os.path.join(self.shared_path, 'visit_reports'),
            os.path.join(self.shared_path, 'lab_reports'),
            os.path.join(self.shared_path, 'supplier_reports')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def guardar_en_biblioteca(self, docx_path: str, pdf_path: str, contexto: Dict[str, Any]) -> Dict[str, str]:
        """
        Guardar documentos en la biblioteca con metadatos
        
        Args:
            docx_path: Ruta del archivo Word
            pdf_path: Ruta del archivo PDF
            contexto: Contexto del documento
            
        Returns:
            Diccionario con rutas de archivos guardados
        """
        try:
            # Determinar tipo de documento
            doc_type = self._determinar_tipo_documento(contexto)
            
            # Crear estructura de carpetas por fecha
            fecha = datetime.now().strftime("%Y-%m")
            fecha_path = os.path.join(self.library_path, doc_type, fecha)
            os.makedirs(fecha_path, exist_ok=True)
            
            # Generar nombres de archivos únicos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{doc_type}_{timestamp}"
            
            # Rutas de destino
            dest_docx = os.path.join(fecha_path, f"{base_name}.docx")
            dest_pdf = os.path.join(fecha_path, f"{base_name}.pdf")
            
            # Copiar archivos
            shutil.copy2(docx_path, dest_docx)
            shutil.copy2(pdf_path, dest_pdf)
            
            # Crear metadatos
            metadatos = {
                'tipo_documento': doc_type,
                'fecha_creacion': datetime.now().isoformat(),
                'archivo_docx': dest_docx,
                'archivo_pdf': dest_pdf,
                'contexto': contexto,
                'tamaño_docx': os.path.getsize(dest_docx),
                'tamaño_pdf': os.path.getsize(dest_pdf)
            }
            
            # Guardar metadatos
            metadatos_path = os.path.join(fecha_path, f"{base_name}_metadata.json")
            with open(metadatos_path, 'w', encoding='utf-8') as f:
                json.dump(metadatos, f, indent=2, ensure_ascii=False)
            
            # Copiar a carpeta compartida
            self._copiar_a_compartida(dest_docx, dest_pdf, doc_type)
            
            logger.info(f"Documentos guardados en biblioteca: {fecha_path}")
            
            return {
                'docx': dest_docx,
                'pdf': dest_pdf,
                'metadatos': metadatos_path
            }
            
        except Exception as e:
            logger.error(f"Error guardando en biblioteca: {str(e)}")
            raise
    
    def _determinar_tipo_documento(self, contexto: Dict[str, Any]) -> str:
        """
        Determinar tipo de documento basado en el contexto
        
        Args:
            contexto: Contexto del documento
            
        Returns:
            Tipo de documento
        """
        if 'incident_code' in contexto:
            return 'incidents'
        elif 'order_number' in contexto:
            return 'visit_reports'
        elif 'report_number' in contexto and 'technical_expert_name' in contexto:
            return 'lab_reports'
        elif 'supplier_name' in contexto:
            return 'supplier_reports'
        else:
            return 'general'
    
    def _copiar_a_compartida(self, docx_path: str, pdf_path: str, doc_type: str):
        """
        Copiar archivos a carpeta compartida
        
        Args:
            docx_path: Ruta del archivo Word
            pdf_path: Ruta del archivo PDF
            doc_type: Tipo de documento
        """
        try:
            # Crear directorio compartido
            shared_dir = os.path.join(self.shared_path, doc_type)
            os.makedirs(shared_dir, exist_ok=True)
            
            # Copiar archivos
            shared_docx = os.path.join(shared_dir, os.path.basename(docx_path))
            shared_pdf = os.path.join(shared_dir, os.path.basename(pdf_path))
            
            shutil.copy2(docx_path, shared_docx)
            shutil.copy2(pdf_path, shared_pdf)
            
            logger.info(f"Archivos copiados a carpeta compartida: {shared_dir}")
            
        except Exception as e:
            logger.warning(f"Error copiando a carpeta compartida: {str(e)}")
    
    def obtener_biblioteca(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de documentos en la biblioteca
        
        Returns:
            Lista de documentos con metadatos
        """
        try:
            documentos = []
            
            # Recorrer directorios de la biblioteca
            for root, dirs, files in os.walk(self.library_path):
                for file in files:
                    if file.endswith('_metadata.json'):
                        metadatos_path = os.path.join(root, file)
                        
                        try:
                            with open(metadatos_path, 'r', encoding='utf-8') as f:
                                metadatos = json.load(f)
                            
                            # Verificar que los archivos existen
                            if (os.path.exists(metadatos.get('archivo_docx', '')) and 
                                os.path.exists(metadatos.get('archivo_pdf', ''))):
                                documentos.append(metadatos)
                            
                        except Exception as e:
                            logger.warning(f"Error cargando metadatos {metadatos_path}: {str(e)}")
            
            # Ordenar por fecha de creación
            documentos.sort(key=lambda x: x.get('fecha_creacion', ''), reverse=True)
            
            return documentos
            
        except Exception as e:
            logger.error(f"Error obteniendo biblioteca: {str(e)}")
            return []
    
    def get_library_path(self, file_path: str) -> str:
        """
        Obtener ruta en la biblioteca para un archivo
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Ruta en la biblioteca
        """
        try:
            # Buscar archivo en la biblioteca
            for root, dirs, files in os.walk(self.library_path):
                for file in files:
                    if file == os.path.basename(file_path):
                        return os.path.join(root, file)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error obteniendo ruta de biblioteca: {str(e)}")
            return file_path
    
    def buscar_documentos(self, criterios: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Buscar documentos por criterios
        
        Args:
            criterios: Criterios de búsqueda
            
        Returns:
            Lista de documentos que coinciden
        """
        try:
            todos_documentos = self.obtener_biblioteca()
            documentos_filtrados = []
            
            for documento in todos_documentos:
                contexto = documento.get('contexto', {})
                
                # Verificar criterios
                coincide = True
                for clave, valor in criterios.items():
                    if clave in contexto:
                        if isinstance(valor, str):
                            if valor.lower() not in str(contexto[clave]).lower():
                                coincide = False
                                break
                        else:
                            if contexto[clave] != valor:
                                coincide = False
                                break
                    else:
                        coincide = False
                        break
                
                if coincide:
                    documentos_filtrados.append(documento)
            
            return documentos_filtrados
            
        except Exception as e:
            logger.error(f"Error buscando documentos: {str(e)}")
            return []
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la biblioteca
        
        Returns:
            Estadísticas de documentos
        """
        try:
            documentos = self.obtener_biblioteca()
            
            estadisticas = {
                'total_documentos': len(documentos),
                'por_tipo': {},
                'por_mes': {},
                'tamaño_total': 0
            }
            
            for documento in documentos:
                # Contar por tipo
                tipo = documento.get('tipo_documento', 'desconocido')
                estadisticas['por_tipo'][tipo] = estadisticas['por_tipo'].get(tipo, 0) + 1
                
                # Contar por mes
                fecha = documento.get('fecha_creacion', '')
                if fecha:
                    mes = fecha[:7]  # YYYY-MM
                    estadisticas['por_mes'][mes] = estadisticas['por_mes'].get(mes, 0) + 1
                
                # Sumar tamaños
                estadisticas['tamaño_total'] += documento.get('tamaño_docx', 0)
                estadisticas['tamaño_total'] += documento.get('tamaño_pdf', 0)
            
            return estadisticas
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}
    
    def limpiar_archivos_temporales(self):
        """
        Limpiar archivos temporales
        """
        try:
            temp_path = os.path.join(self.base_path, 'temp')
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
                os.makedirs(temp_path, exist_ok=True)
            
            logger.info("Archivos temporales limpiados")
            
        except Exception as e:
            logger.error(f"Error limpiando archivos temporales: {str(e)}")
    
    def exportar_biblioteca(self, destino: str) -> bool:
        """
        Exportar biblioteca completa a ubicación externa
        
        Args:
            destino: Ruta de destino para la exportación
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            # Crear directorio de destino
            os.makedirs(destino, exist_ok=True)
            
            # Copiar biblioteca completa
            shutil.copytree(self.library_path, os.path.join(destino, 'library'))
            
            # Copiar carpeta compartida
            shutil.copytree(self.shared_path, os.path.join(destino, 'shared'))
            
            logger.info(f"Biblioteca exportada a: {destino}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando biblioteca: {str(e)}")
            return False
    
    def importar_biblioteca(self, origen: str) -> bool:
        """
        Importar biblioteca desde ubicación externa
        
        Args:
            origen: Ruta de origen de la biblioteca
            
        Returns:
            True si la importación fue exitosa
        """
        try:
            # Verificar que existe la biblioteca
            if not os.path.exists(os.path.join(origen, 'library')):
                logger.error("Biblioteca de origen no encontrada")
                return False
            
            # Hacer backup de la biblioteca actual
            backup_path = f"{self.library_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.library_path):
                shutil.move(self.library_path, backup_path)
            
            # Copiar nueva biblioteca
            shutil.copytree(os.path.join(origen, 'library'), self.library_path)
            
            # Copiar carpeta compartida si existe
            if os.path.exists(os.path.join(origen, 'shared')):
                shutil.copytree(os.path.join(origen, 'shared'), self.shared_path)
            
            logger.info(f"Biblioteca importada desde: {origen}")
            return True
            
        except Exception as e:
            logger.error(f"Error importando biblioteca: {str(e)}")
            return False
