import logging
from django.core.cache import cache
from apps.sap_integration.models import ServiceCall, BusinessPartner, Project

logger = logging.getLogger(__name__)

class SAPQueryService:
    """
    Servicio para consultas READ-ONLY a SAP (PRDPOLIFUSION)
    Utiliza conexión 'sap_db' configurada en settings.
    """
    
    CACHE_TIMEOUT = 3600  # 1 hora para maestros
    SHORT_CACHE = 300     # 5 minutos para búsquedas
    
    def get_customer_by_code(self, card_code):
        """Obtener cliente por código (CardCode)"""
        cache_key = f'sap_customer_{card_code}'
        
        # Intentar desde cache
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            customer = BusinessPartner.objects.using('sap_db').get(
                card_code=card_code
            )
            
            data = {
                'card_code': customer.card_code,
                'card_name': customer.card_name,
                'email': customer.email_address,
                'phone': customer.phone1,
                'card_type': customer.card_type
            }
            
            # Guardar en cache
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
            
            return data
            
        except BusinessPartner.DoesNotExist:
            logger.warning(f"Customer {card_code} not found in SAP")
            return None
        except Exception as e:
            logger.error(f"Error fetching customer {card_code}: {e}")
            return None
    
    def search_customers(self, query):
        """Buscar clientes por nombre o código"""
        cache_key = f'sap_customer_search_{query}'
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # Buscar por nombre o código
            # Nota: SAP HANA case sensitivity puede variar, usando icontains por si acaso
            customers = BusinessPartner.objects.using('sap_db').filter(
                card_name__icontains=query,
                card_type='C'  # Solo clientes
            )[:20]  # Limitar resultados
            
            data = [{
                'card_code': c.card_code,
                'card_name': c.card_name,
                'email': c.email_address,
                'phone': c.phone1,
            } for c in customers]
            
            cache.set(cache_key, data, self.SHORT_CACHE)
            return data
            
        except Exception as e:
            logger.error(f"Error searching customers '{query}': {e}")
            return []
    
    def get_service_call(self, call_id):
        """Obtener llamada de servicio por ID"""
        # Las llamadas de servicio cambian frecuentemente, no cacheamos por mucho tiempo
        # o mejor, no cacheamos si queremos datos realtime
        try:
            call = ServiceCall.objects.using('sap_db').get(call_id=call_id)
            
            # Obtener datos del cliente asociado
            customer_data = None
            if call.customer_code:
                customer_data = self.get_customer_by_code(call.customer_code)
            
            # Obtener nombre del contacto desde OCPR
            contact_name = None
            if call.contact_code:
                try:
                    from django.db import connections
                    with connections['sap_db'].cursor() as cursor:
                        cursor.execute("""
                            SELECT Name FROM OCPR WHERE CntctCode = %s
                        """, [call.contact_code])
                        row = cursor.fetchone()
                        if row:
                            contact_name = row[0]
                except Exception as e:
                    logger.warning(f"Could not fetch contact name for code {call.contact_code}: {e}")
            

            # Obtener nombre del técnico desde OHEM
            technician_name = getattr(call, 'technician', None)
            if technician_name:
                # Asegurar que es string para verificación, o simplemente usarlo si es int
                technician_id_val = str(technician_name)
                if technician_id_val.isdigit():
                    try:
                        from django.db import connections
                        with connections['sap_db'].cursor() as cursor:
                            cursor.execute("""
                                SELECT firstName, lastName FROM OHEM WHERE empID = %s
                            """, [technician_name])
                            row = cursor.fetchone()
                            if row:
                                technician_name = f"{row[0]} {row[1]}"
                    except Exception as e:
                        logger.warning(f"Could not fetch technician name for ID {technician_name}: {e}")

            # Obtener datos de la OBRA/PROYECTO (@FRMOBRAS)
            project_data = {}
            if call.bp_project_code:
                try:
                    project = Project.objects.using('sap_db').get(code=call.bp_project_code)
                    project_data = {
                        'address': project.address,
                        'commune': project.commune,
                        'city': project.city,
                        'installer_name': project.installer_name,
                        'installer_phone': project.installer_phone,
                        'construction_company': project.construction_company,
                        'admin_name': project.admin_name,
                        'prof_obra': project.prof_obra_nom,
                        'ito': project.ito_nom,
                        'otros_nom': project.otros_nom
                    }
                except Project.DoesNotExist:
                    logger.warning(f"Project {call.bp_project_code} not found in SAP")
                except Exception as e:
                    logger.error(f"Error fetching project data: {e}")

            return {
                'call_id': call.call_id,
                'subject': call.subject,
                'customer_code': call.customer_code,
                'customer_name': call.customer_name,
                'customer_data': customer_data,
                'status': call.status,
                'create_date': call.create_date,
                # Campos mapeados recientemente
                'technician': technician_name, # AHORA CON NOMBRE REAL
                'technician_id': getattr(call, 'technician', None), # Guardamos el ID por si acaso
                'description': getattr(call, 'description', None),
                'problem_type': getattr(call, 'problem_type', None),
                
                # Campos UDFs (Deep Integration)
                'project_code': getattr(call, 'bp_project_code', None),
                'project_name': getattr(call, 'project_name_udf', None),
                'salesperson': getattr(call, 'salesperson_name', None),
                'mezclado': getattr(call, 'mezclado_int', None),
                'telephone': getattr(call, 'telephone', None),
                'address': project_data.get('address') or getattr(call, 'bp_ship_addr', None), # Priorizar Obra
                'commune': project_data.get('commune'),
                'city': project_data.get('city'),
                'contact_code': getattr(call, 'contact_code', None),
                'contact_name': contact_name,
                'assignee': getattr(call, 'assignee', None),
                
                # Datos Extra de Obra
                'installer_name': project_data.get('installer_name'),
                'installer_phone': project_data.get('installer_phone'),
                'construction_company': project_data.get('construction_company'),
                'admin_name': project_data.get('admin_name'),
                'prof_obra': project_data.get('prof_obra'),
                'ito': project_data.get('ito'),
                'otros_nom': project_data.get('otros_nom'),
                
                # Observaciones Específicas
                'general_observations': getattr(call, 'obs_general', None),
                'obs_muro': getattr(call, 'obs_muro', None),
                'obs_matriz': getattr(call, 'obs_matriz', None),
                'obs_losa': getattr(call, 'obs_losa', None),
                'obs_almac': getattr(call, 'obs_almac', None),
                'obs_pre_arm': getattr(call, 'obs_pre_arm', None),
                'obs_exter': getattr(call, 'obs_exter', None),
            }
            
        except ServiceCall.DoesNotExist:
            logger.warning(f"Service call {call_id} not found in SAP")
            return None
        except Exception as e:
            logger.error(f"Error fetching service call {call_id}: {e}")
            return None
    
    def get_customer_projects(self, card_code):
        """Obtener obras de un cliente"""
        cache_key = f'sap_projects_{card_code}'
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            projects = Project.objects.using('sap_db').filter(
                card_code=card_code
            )
            
            data = [{
                'code': p.code,
                'name': p.name,
            } for p in projects]
            
            cache.set(cache_key, data, self.CACHE_TIMEOUT)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching projects for {card_code}: {e}")
            return []
    
    @staticmethod
    def get_attachments(call_id):
        """
        Obtiene lista de adjuntos para una llamada de servicio desde ATC1
        """
        from django.db import connections
        try:
            # Primero obtener el AtcEntry de la llamada
            with connections['sap_db'].cursor() as cursor:
                cursor.execute("SELECT AtcEntry FROM OSCL WHERE callID = %s", [call_id])
                row = cursor.fetchone()
                
                if not row or not row[0]:
                    return []
                
                atc_entry = row[0]
                
                # Ahora buscar en ATC1
                cursor.execute("""
                    SELECT Line, trgtPath, FileName, FileExt, Date 
                    FROM ATC1 
                    WHERE AbsEntry = %s
                """, [atc_entry])
                
                attachments = []
                for res in cursor.fetchall():
                    line, path, name, ext, date = res
                    full_name = f"{name}.{ext}" if ext else name
                    # Limpiar ruta (a veces viene sin backslash final)
                    clean_path = path.rstrip('\\')
                    full_path = f"{clean_path}\\{full_name}"
                    
                    attachments.append({
                        'id': f"{atc_entry}_{line}", # ID compuesto para uso en frontend/API
                        'line': line,
                        'atc_entry': atc_entry,
                        'filename': full_name,
                        'path': full_path,
                        'date': date,
                        'is_image': ext.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp'] if ext else False
                    })
                    
                return attachments
                
        except Exception as e:
            logger.error(f"Error fetching attachments: {e}")
            return []

    @staticmethod
    def get_attachment_file(atc_entry, line):
        """
        Retorna el contenido binario de un archivo adjunto y su mime type
        """
        import mimetypes
        import os
        from django.db import connections
        
        try:
            with connections['sap_db'].cursor() as cursor:
                cursor.execute("""
                    SELECT trgtPath, FileName, FileExt 
                    FROM ATC1 
                    WHERE AbsEntry = %s AND Line = %s
                """, [atc_entry, line])
                row = cursor.fetchone()
                
                if not row:
                    return None, None, None
                
                path, name, ext = row
                full_name = f"{name}.{ext}" if ext else name
                clean_path = path.rstrip('\\')
                full_path = f"{clean_path}\\{full_name}"
                
                if not os.path.exists(full_path):
                    # Intentar corregir rutas de red o mapeos locales si fallara
                    # Por ahora devolvemos error si no existe
                     return None, None, f"Archivo no encontrado en ruta: {full_path}"
                
                # Adivinar mimetype
                mime_type, _ = mimetypes.guess_type(full_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                    
                # Leer archivo
                with open(full_path, 'rb') as f:
                    content = f.read()
                    
                return content, mime_type, full_name
                
        except Exception as e:
            return None, None, str(e)
