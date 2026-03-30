import logging
from django.core.cache import cache
from apps.core.thread_local import get_current_country
from django.db import connections
from .models import ServiceCall, BusinessPartner, Project

logger = logging.getLogger(__name__)

class SAPQueryService:
    """
    Servicio para consultas READ-ONLY a SAP.
    Rutea dinámicamente a PRDPOLIFUSION (CL), PRDPOLPERU (PE) o PRDPOLCOLOMBIA (CO)
    según el contexto del hilo actual.
    """
    
    def _get_db_alias(self):
        """Determina el alias de la base de datos SAP según el contexto."""
        country = get_current_country()
        alias = 'sap_db' # Default CL
        if country == 'PE':
            alias = 'sap_db_pe'
        elif country == 'CO':
            alias = 'sap_db_co'
            
        logger.info(f"[SAPQueryService] DB Routing: {country} -> {alias}")
        return alias
    
    def get_employee_id_by_name(self, name):
        """Busca el empID de un empleado por su nombre completo (firstName + lastName)."""
        if not name: return None
        
        cache_key = f'sap_emp_id_{get_current_country()}_{name.replace(" ", "_").upper()}'
        cached = cache.get(cache_key)
        if cached: return cached
        
        try:
            with connections[self._get_db_alias()].cursor() as cursor:
                # Búsqueda flexible de nombre completo
                search_val = f'%{name.strip()}%'
                query = "SELECT TOP 1 empID FROM OHEM WHERE (firstName + ' ' + lastName) LIKE %s AND Active='Y'"
                cursor.execute(query, [search_val])
                row = cursor.fetchone()
                if row:
                    cache.set(cache_key, row[0], 3600)
                    return row[0]
                
                # Segunda oportunidad: partes
                parts = name.strip().split(' ')
                if len(parts) >= 2:
                    query = "SELECT TOP 1 empID FROM OHEM WHERE firstName LIKE %s AND lastName LIKE %s AND Active='Y'"
                    cursor.execute(query, [f'%{parts[0]}%', f'%{parts[-1]}%'])
                    row = cursor.fetchone()
                    if row:
                        cache.set(cache_key, row[0], 3600)
                        return row[0]
        except Exception as e:
            logger.error(f"Error looking up employee ID for {name}: {e}")
            
        return None
    
    def get_salesperson_id_by_name(self, name):
        """Busca el SlpCode de un vendedor (OSLP) por su nombre."""
        if not name: return None
        
        cache_key = f'sap_slp_id_{get_current_country()}_{name.replace(" ", "_").upper()}'
        cached = cache.get(cache_key)
        if cached: return cached
        
        try:
            with connections[self._get_db_alias()].cursor() as cursor:
                query = "SELECT TOP 1 SlpCode FROM OSLP WHERE SlpName LIKE %s AND (Active = 'Y' OR SlpCode > 0)"
                cursor.execute(query, [f'%{name.strip()}%'])
                row = cursor.fetchone()
                if row:
                    cache.set(cache_key, row[0], 3600)
                    return row[0]
        except Exception as e:
            logger.error(f"Error looking up salesperson ID for {name}: {e}")
            
        return None
    
    CACHE_TIMEOUT = 3600  # 1 hora para maestros
    SHORT_CACHE = 300     # 5 minutos para búsquedas
    
    def get_customer_info(self, card_code):
        """Obtener información extendida del cliente para automatización (Técnico, Vendedor)"""
        cache_key = f'sap_customer_info_{get_current_country()}_{card_code}'
        cached = cache.get(cache_key)
        if cached: return cached

        try:
            with connections[self._get_db_alias()].cursor() as cursor:
                # Determinar si el campo Technician existe (Varia por localización/versión)
                country = get_current_country()
                tech_field = "Technician"
                if country == 'PE':
                    # En Perú parece no existir o tener otro nombre, omitir por ahora si falla
                    query = "SELECT CardName, SlpCode, E_Mail, Phone1 FROM OCRD WHERE CardCode = %s"
                    cursor.execute(query, [card_code])
                else:
                    try:
                        query = "SELECT CardName, SlpCode, Technician, E_Mail, Phone1 FROM OCRD WHERE CardCode = %s"
                        cursor.execute(query, [card_code])
                    except Exception:
                        # Fallback si falla por columna 'Technician'
                        query = "SELECT CardName, SlpCode, E_Mail, Phone1 FROM OCRD WHERE CardCode = %s"
                        cursor.execute(query, [card_code])
                
                row = cursor.fetchone()
                if not row: return None

                # Mapear columnas según el query ejecutado
                if len(row) == 5: # Chile / Estándar con Technician
                    data = {
                        'card_code': card_code,
                        'card_name': row[0],
                        'SalesEmployeeCode': row[1],
                        'TechnicianCode': row[2],
                        'email': row[3],
                        'phone': row[4]
                    }
                else: # Perú u otros sin Technician
                    data = {
                        'card_code': card_code,
                        'card_name': row[0],
                        'SalesEmployeeCode': row[1],
                        'TechnicianCode': None,
                        'email': row[2],
                        'phone': row[3]
                    }
                
                cache.set(cache_key, data, self.CACHE_TIMEOUT)
                return data
        except Exception as e:
            logger.error(f"Error fetching customer info for {card_code}: {e}")
            return None

    def get_customer_by_code(self, card_code):
        """Alias retrocompatible para obtener cliente básico"""
        return self.get_customer_info(card_code)
    
    def search_customers(self, query):
        """Buscar clientes por nombre o código"""
        cache_key = f'sap_customer_search_{get_current_country()}_{query}'
        
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            from django.db.models import Q
            # Buscar por nombre o código
            customers = BusinessPartner.objects.using(self._get_db_alias()).filter(
                Q(card_name__icontains=query) | Q(card_code__icontains=query),
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

    def get_sales_employees(self):
        """Obtener lista de vendedores activos (OSLP)"""
        cache_key = f'sap_sales_employees_{get_current_country()}'
        
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        try:
            from django.db import connections
            with connections[self._get_db_alias()].cursor() as cursor:
                # Ampliar búsqueda para incluir UDFs si existen o relajar filtros si es necesario
                cursor.execute("SELECT SlpCode, SlpName, Email FROM OSLP WHERE Active = 'Y' OR SlpCode > 0 ORDER BY SlpName")
                employees = [{'code': row[0], 'name': row[1], 'email': row[2]} for row in cursor.fetchall()]
                
            cache.set(cache_key, employees, self.CACHE_TIMEOUT)
            return employees
                
        except Exception as e:
            logger.error(f"Error fetching sales employees: {e}")
            return []

    def get_technicians(self, only_technical_role=False):
        """
        Obtener lista de técnicos/empleados activos (OHEM) vía Service Layer (SL) o SQL.
        param only_technical_role: Si es True, filtra solo aquellos con rol técnico oficial en SAP.
        """
        cache_key = f'sap_technicians_{get_current_country()}_{"tech_only" if only_technical_role else "all"}'
        
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Intentar vía Service Layer (Usando Transaction Service que ya maneja SL)
        country = get_current_country()
        if country not in ('PE', 'CO') and not only_technical_role:
            try:
                from .sap_transaction_service import SAPTransactionService
                sap_tx = SAPTransactionService()
                technicians = sap_tx.get_technicians()
                if technicians:
                    cache.set(cache_key, technicians, self.CACHE_TIMEOUT)
                    return technicians
            except Exception as sl_err:
                logger.error(f"Error fetching technicians via SL: {sl_err}")

        # Fallback o Forzado a SQL si se requiere filtrado fino o SL falla
        try:
            technicians = []
            with connections[self._get_db_alias()].cursor() as cursor:
                if country == 'PE':
                    # En Perú filtrar por posición para asegurar que SAP los acepte en Service Calls
                    # IDs: 1 (Ventas), 3 (Coordinación), 5 (SERTEC)
                    query = """
                        SELECT empID, (firstName + ' ' + lastName) as Name, email 
                        FROM OHEM 
                        WHERE Active = 'Y' 
                        AND (position IS NOT NULL OR empID = 13)
                        ORDER BY firstName, lastName
                    """
                elif country == 'CO':
                    # En Colombia (TSTPOLCOLOMBIA_2), los 'Responsables' en SAP (Tratado por)
                    # se alimentan de la tabla de Usuarios (OUSR), no solo de Empleados.
                    query = """
                        SELECT USERID, U_NAME as Name, E_Mail 
                        FROM OUSR 
                        ORDER BY U_NAME
                    """
                else:
                    # Chile suele tener el flag 'technician' habilitado nativamente
                    where_clause = "WHERE Active = 'Y'"
                    if only_technical_role:
                        where_clause += " AND technician = 'Y'"
                    query = f"SELECT empID, (firstName + ' ' + lastName) as Name, email FROM OHEM {where_clause} ORDER BY firstName, lastName"
                
                try:
                    cursor.execute(query)
                except Exception as e:
                    # Fallback final a todos los empleados activos si falla lo anterior
                    logger.warning(f"Error en query de técnicos específica ({country}): {e}. Falling back to all active employees.")
                    query = "SELECT empID, (firstName + ' ' + lastName) as Name, email FROM OHEM WHERE Active = 'Y' ORDER BY firstName, lastName"
                    cursor.execute(query)

                rows = cursor.fetchall()
                for row in rows:
                    technicians.append({
                        'id': row[0],
                        'name': row[1].strip() if row[1] else f"Tech {row[0]}",
                        'email': row[2] or ''
                    })
                
            if technicians:
                cache.set(cache_key, technicians, self.CACHE_TIMEOUT)
            return technicians
        except Exception as sql_err:
            logger.error(f"Error fetching technicians via SQL fallback: {sql_err}")
            
        # Fallback final manual para Colombia (mientras se resuelven permisos SAP o datos vacíos)
        if get_current_country() == 'CO':
            logger.info("SAP: Usando fallback manual para técnicos de Colombia.")
            return [
                {'id': 1, 'name': 'CRISTIAN PEÑA', 'email': ''},
                {'id': 2, 'name': 'CRISTIAN PEÑA (V2)', 'email': ''},
            ]
        return []
    
    def get_customer_full_details(self, card_code):
        """
        Obtener detalles completos del cliente incluyendo:
        - Datos básicos (OCRD)
        - Vendedor asignado (OSLP)
        - Direcciones de envío (CRD1)
        - Proyectos/Obras (si existe tabla @FRMOBRAS)
        """
        cache_key = f'sap_customer_details_{get_current_country()}_{card_code}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            from django.db import connections
            with connections[self._get_db_alias()].cursor() as cursor:
                # 1. Datos básicos del cliente + vendedor
                cursor.execute("""
                    SELECT 
                        c.CardCode, 
                        c.CardName, 
                        c.SlpCode,
                        s.SlpName,
                        s.Email as SalespersonEmail,
                        c.Address,
                        c.Phone1,
                        c.E_Mail
                    FROM OCRD c
                    LEFT JOIN OSLP s ON c.SlpCode = s.SlpCode
                    WHERE c.CardCode = %s
                """, [card_code])
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"Customer {card_code} not found in SAP")
                    return None
                
                customer_data = {
                    'card_code': row[0],
                    'card_name': row[1],
                    'salesperson_code': row[2],
                    'salesperson_name': row[3],
                    'salesperson_email': row[4],
                    'address': row[5],
                    'phone': row[6],
                    'email': row[7],
                    'addresses': [],
                    'projects': []
                }
                
                # 2. Direcciones de envío (CRD1)
                cursor.execute("""
                    SELECT 
                        Address,
                        Street,
                        City,
                        AdresType
                    FROM CRD1
                    WHERE CardCode = %s AND AdresType = 'S'
                    ORDER BY Address
                """, [card_code])
                
                customer_data['addresses'] = [{
                    'address_name': addr[0],
                    'street': addr[1],
                    'city': addr[2],
                    'type': addr[3]
                } for addr in cursor.fetchall()]
                
                # 3. Proyectos/Obras (intentar consultar @FRMOBRAS)
                try:
                    # Limpiar card_code para búsqueda flexible (quitar C prefijo si existe)
                    clean_code = card_code[1:] if card_code.startswith('C') else card_code
                    
                    cursor.execute("""
                        SELECT 
                            Name,
                            Code,
                            U_nx_direccion,
                            U_nx_comuna,
                            U_nx_ciudad
                        FROM [@FRMOBRAS]
                        WHERE U_nx_cardcode LIKE %s
                        ORDER BY Name
                    """, [f'%{clean_code}%'])
                    
                    customer_data['projects'] = [{
                        'obra': proj[0] or 'Sin Nombre',
                        'proyecto': proj[1] or 'S/P',
                        'direccion': proj[2] or '',
                        'comuna': proj[3] or '',
                        'ciudad': proj[4] or ''
                    } for proj in cursor.fetchall()]
                except Exception as proj_error:
                    logger.debug(f"Could not fetch projects from @FRMOBRAS for {card_code}: {proj_error}")
                    customer_data['projects'] = []

                # 4. Fallback/Complemento: Si no hay proyectos en @FRMOBRAS, usar direcciones de envío (CRD1) como "obras"
                if not customer_data['projects'] and customer_data['addresses']:
                    customer_data['projects'] = [{
                        'obra': addr['address_name'],
                        'proyecto': '',
                        'direccion': addr['street'],
                        'comuna': '',
                        'ciudad': addr['city']
                    } for addr in customer_data['addresses']]
                # Si ambos existen, podríamos querer combinarlos o priorizar @FRMOBRAS
                elif customer_data['addresses']:
                    # Opcional: Agregar direcciones que no estén ya como obras?
                    # Por ahora mantengamos la lógica simple: si hay @FRMOBRAS, se usa eso.
                    pass
            
            # Cache por 1 hora
            cache.set(cache_key, customer_data, 3600)
            return customer_data
                
        except Exception as e:
            logger.error(f"Error fetching customer details for {card_code}: {e}")
            return None
    
    SERVICE_CALL_CACHE = 60  # 60 segundos para datos de SC (balance frescura/velocidad)

    def get_service_call(self, doc_num):
        """Obtener llamada de servicio por DocNum"""
        country = get_current_country() or 'CL'
        cache_key = f'sap_sc_{country}_{doc_num}'
        
        # Intentar desde cache (TTL corto: datos semi-realtime)
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Cache HIT para SC {doc_num} [{country}]")
            return cached

        try:
            query = ServiceCall.objects.using(self._get_db_alias())
            
            # Excluir columnas UDF avanzadas que solo existen en Chile para evitar Crash SQLExecDirectW - Invalid Column Name
            if country != 'CL':
                query = query.defer(
                    'sap_category_udf', 'sap_subcategory_udf', 
                    'obra_otro_proveedor', 'nivel_instalacion', 
                    'otro_proveedor'
                )
                
                # 'obs_critica' solo está en CL y CO, no en PE
                if country == 'PE':
                    query = query.defer('obs_critica')
                
            call = query.get(doc_num=doc_num)
            
            # Obtener datos del cliente asociado
            customer_data = None
            if call.customer_code:
                customer_data = self.get_customer_by_code(call.customer_code)
            
            # Obtener nombre del contacto desde OCPR
            contact_name = None
            if call.contact_code:
                try:
                    from django.db import connections
                    with connections[self._get_db_alias()].cursor() as cursor:
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
                technician_id_val = str(technician_name)
                if technician_id_val.isdigit():
                    try:
                        from django.db import connections
                        with connections[self._get_db_alias()].cursor() as cursor:
                            cursor.execute("""
                                SELECT firstName, lastName FROM OHEM WHERE empID = %s
                            """, [technician_name])
                            row = cursor.fetchone()
                            if row:
                                technician_name = f"{row[0]} {row[1]}"
                    except Exception as e:
                        logger.warning(f"Could not fetch technician name for ID {technician_name}: {e}")

            # Obtener nombre del vendedor desde OSLP
            salesperson_name = getattr(call, 'salesperson_name', None)
            if salesperson_name:
                salesperson_id_val = str(salesperson_name)
                if salesperson_id_val.isdigit():
                    try:
                        from django.db import connections
                        with connections[self._get_db_alias()].cursor() as cursor:
                            cursor.execute("""
                                SELECT SlpName FROM OSLP WHERE SlpCode = %s
                            """, [salesperson_name])
                            row = cursor.fetchone()
                            if row:
                                salesperson_name = row[0]
                    except Exception as e:
                        logger.warning(f"Could not fetch salesperson name for ID {salesperson_name}: {e}")

            # Obtener datos de la OBRA/PROYECTO (@FRMOBRAS)
            project_data = {}
            if call.bp_project_code:
                try:
                    project_query = Project.objects.using(self._get_db_alias())
                    
                    # Deferir columnas que no existen en el @FRMOBRAS de Perú para evitar 42S22 SQL Error
                    if country == 'PE':
                        project_query = project_query.defer(
                            'prof_obra_nom', 'ito_nom', 'otros_nom'
                        )
                    
                    project = project_query.get(code=call.bp_project_code)
                    project_data = {
                        'address': project.address,
                        'commune': project.commune,
                        'city': project.city,
                        'installer_name': project.installer_name,
                        'installer_phone': project.installer_phone,
                        'construction_company': project.construction_company,
                        'admin_name': project.admin_name,
                        # Solo acceder si no están deferidos (para evitar recarga de SQL fatal)
                        'prof_obra': getattr(project, 'prof_obra_nom', None) if country != 'PE' else None,
                        'ito': getattr(project, 'ito_nom', None) if country != 'PE' else None,
                        'otros_nom': getattr(project, 'otros_nom', None) if country != 'PE' else None
                    }
                except Project.DoesNotExist:
                    logger.warning(f"Project {call.bp_project_code} not found in SAP")
                except Exception as e:
                    logger.error(f"Error fetching project data: {e}")

            result = {
                'call_id': call.call_id,
                'doc_num': doc_num,
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
                'salesperson': salesperson_name,
                'mezclado': getattr(call, 'mezclado_int', None),
                'telephone': getattr(call, 'telephone', None),
                'address': project_data.get('address') or getattr(call, 'ship_street', None) or getattr(call, 'bp_ship_addr', None),
                'commune': project_data.get('commune') or getattr(call, 'ship_county', None),
                'city': project_data.get('city') or getattr(call, 'ship_city', None),
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
                
                # Campos nuevos (Mapeo Completo) - Acceso condicional para evitar crashes en PE/CO
                'ship_address': getattr(call, 'bp_ship_addr', None),
                'sap_category': getattr(call, 'sap_category_udf', None) if country == 'CL' else None,
                'sap_subcategory': getattr(call, 'sap_subcategory_udf', None) if country == 'CL' else None,
                'sap_priority': getattr(call, 'priority_raw', None),
                'create_time': f"{getattr(call, 'create_time_raw', 0) // 60:02d}:{getattr(call, 'create_time_raw', 0) % 60:02d}" if getattr(call, 'create_time_raw', None) is not None else None,
                
                # Datos de Máquinas Vectoriales
                'retiro_maq': getattr(call, 'retiro_maq', None),
                'maq1': getattr(call, 'maq1', None), 'ini1': getattr(call, 'ini1', None), 'cor1': getattr(call, 'cor1', None),
                'maq2': getattr(call, 'maq2', None), 'ini2': getattr(call, 'ini2', None), 'cor2': getattr(call, 'cor2', None),
                'maq3': getattr(call, 'maq3', None), 'ini3': getattr(call, 'ini3', None), 'cor3': getattr(call, 'cor3', None),
                'maq4': getattr(call, 'maq4', None), 'ini4': getattr(call, 'ini4', None), 'cor4': getattr(call, 'cor4', None),
                'maq5': getattr(call, 'maq5', None), 'ini5': getattr(call, 'ini5', None), 'cor5': getattr(call, 'cor5', None),
                'maq6': getattr(call, 'maq6', None), 'ini6': getattr(call, 'ini6', None), 'cor6': getattr(call, 'cor6', None),
                
                # UDFs Complementarios Identificados
                'U_NX_MEZCLADO': getattr(call, 'mezclado', None),
                'U_NX_RESCATADA': getattr(call, 'obra_rescatada', None),
                'U_NX_PATENTE': getattr(call, 'patente', None),
                'U_NX_OBRAFINALIZADA': getattr(call, 'obra_finalizada', None),
                'U_NX_FECHAVISITA': getattr(call, 'fecha_visita_udf', None),
                'U_obs_critica': getattr(call, 'obs_critica', None) if country in ('CL', 'CO') else None,
                'U_obra_con_otro_proveedor': getattr(call, 'obra_otro_proveedor', None) if country == 'CL' else None,
                'U_nivel_instalacion': getattr(call, 'nivel_instalacion', None) if country == 'CL' else None,
                'U_otro_proveedor': getattr(call, 'otro_proveedor', None) if country == 'CL' else None,
            }
            
            # Guardar en caché con TTL corto
            cache.set(cache_key, result, self.SERVICE_CALL_CACHE)
            return result

        except ServiceCall.DoesNotExist:
            logger.warning(f"Service call doc_num {doc_num} not found in SAP")
            return None
        except Exception as e:
            logger.error(f"Error fetching service call doc_num {doc_num}: {e}")
            return None
    
    def get_available_udfs(self, table_name):
        """
        Obtiene la lista de campos de usuario (UDFs) disponibles para una tabla en SAP.
        Consulta la tabla CUFD.
        table_name: ej. 'OSCL' para Service Calls
        """
        country = get_current_country()
        cache_key = f'sap_udfs_{country}_{table_name}'
        
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
            
        try:
            udfs = []
            db_alias = self._get_db_alias()
            from django.db import connections
            with connections[db_alias].cursor() as cursor:
                # En CUFD, AliasID es el nombre del campo sin el prefijo 'U_'
                query = "SELECT AliasID FROM CUFD WHERE TableID = %s"
                cursor.execute(query, [table_name])
                rows = cursor.fetchall()
                # Normalizar a prefijo 'U_' para facilitar matching con payloads de Service Layer
                udfs = [f"U_{row[0]}" for row in rows]
                
            # Guardar en caché por 24 horas (el esquema de SAP es estático casi siempre)
            cache.set(cache_key, udfs, 86400)
            logger.info(f"SAP: Detectados {len(udfs)} UDFs para tabla {table_name} en {country}")
            return udfs
        except Exception as e:
            logger.error(f"Error detectando UDFs para tabla {table_name}: {e}")
            return []

    def get_customer_projects(self, card_code):
        """Obtener obras de un cliente (SQL Crudo para evitar discrepancias de esquema)"""
        if not card_code: return []
        
        cache_key = f'sap_projects_{get_current_country()}_{card_code}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # Limpiar card_code: quitar prefijos comunes (C, CL, CO) y espacios
            # Queremos buscar por el núcleo del RUT/NIT
            clean_code = card_code
            for prefix in ['CL', 'CO', 'C']:
                if clean_code.upper().startswith(prefix):
                    clean_code = clean_code[len(prefix):]
                    break
            
            projects = []
            with connections[self._get_db_alias()].cursor() as cursor:
                # Usar LIKE para mayor flexibilidad si el CardCode en @FRMOBRAS no tiene prefijos
                # Se consultan solo las columnas base comunes a todos los países
                query = """
                    SELECT Code, Name, U_nx_direccion, U_nx_comuna, U_nx_ciudad
                    FROM [@FRMOBRAS]
                    WHERE U_nx_cardcode LIKE %s
                    ORDER BY Name
                """
                cursor.execute(query, [f'%{clean_code}%'])
                rows = cursor.fetchall()
                
                for row in rows:
                    projects.append({
                        'proyecto': row[0],
                        'obra': row[1] or 'Sin Nombre',
                        'direccion': row[2] or '',
                        'comuna': row[3] or '',
                        'ciudad': row[4] or '',
                    })
            
            cache.set(cache_key, projects, self.CACHE_TIMEOUT)
            return projects
            
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
            with connections[SAPQueryService()._get_db_alias()].cursor() as cursor:
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

    def get_fallback_technician_id(self):
        """
        Obtiene el primer ID de empleado que tiene un rol en HEM6.
        Útil como 'técnico de respaldo' cuando el original no tiene rol técnico oficial.
        """
        from django.db import connections
        from apps.core.thread_local import get_current_country
        
        country_code = get_current_country()
        db_alias = self._get_db_alias()
        
        logger.info(f"[SAPQueryService] Buscando técnico de respaldo para {country_code} ({db_alias})")
        
        try:
            with connections[db_alias].cursor() as cursor:
                # 1. Intentamos obtener el primer empleado que tenga ROL TECNICO (1) en HEM6
                query = "SELECT TOP 1 empID FROM HEM6 WHERE roleID = 1 ORDER BY empID ASC"
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    logger.info(f"[SAPQueryService] Técnico de respaldo encontrado (HEM6-Tech): {row[0]}")
                    return row[0]
                
                # 2. Fallback CO: Buscar cualquier empleado con ROL en HEM6 (visto en debug con RoleID -2)
                if country_code == 'CO':
                    query = "SELECT TOP 1 empID FROM HEM6 ORDER BY empID ASC"
                    cursor.execute(query)
                    row = cursor.fetchone()
                    if row:
                        logger.info(f"[SAPQueryService] Técnico de respaldo encontrado (Cualquier HEM6 CO): {row[0]}")
                        return row[0]

                # 3. Fallback PE: Buscar por posición SERTEC (5) o Ventas con rol (1)
                if country_code == 'PE':
                    # Probar 31 (Percy Luey - SERTEC) o 13 (Albert - Pos 1)
                    query = "SELECT TOP 1 empID FROM OHEM WHERE Active = 'Y' AND position IN (5, 1) ORDER BY (CASE WHEN position=5 THEN 0 ELSE 1 END), empID ASC"
                    cursor.execute(query)
                    row = cursor.fetchone()
                    if row:
                        logger.info(f"[SAPQueryService] Técnico de respaldo encontrado (Position PE): {row[0]}")
                        return row[0]

                # 4. Fallback General: Empleado con posición cualquiera
                query = "SELECT TOP 1 empID FROM OHEM WHERE Active = 'Y' AND position IS NOT NULL ORDER BY empID ASC"
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    logger.info(f"[SAPQueryService] Técnico de respaldo encontrado (OHEM-Pos): {row[0]}")
                    return row[0]
                    
                # 4. Fallback Final: Primer empleado activo
                query = "SELECT TOP 1 empID FROM OHEM WHERE Active = 'Y' ORDER BY empID ASC"
                cursor.execute(query)
                row = cursor.fetchone()
                if row:
                    return row[0]
                    
        except Exception as e:
            logger.error(f"[SAPQueryService] Error obteniendo técnico de respaldo: {e}")
            
        return None

    @staticmethod
    def get_attachment_file(atc_entry, line):
        """
        Retorna el contenido binario de un archivo adjunto y su mime type
        """
        import mimetypes
        import os
        from django.db import connections
        
        try:
            with connections[SAPQueryService()._get_db_alias()].cursor() as cursor:
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
