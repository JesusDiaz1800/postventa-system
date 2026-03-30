import requests
import logging
import json
import time
import os
from filelock import FileLock
from django.conf import settings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor
import threading
from apps.core.thread_local import get_current_country

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class SAPTransactionService:
    """
    Servicio para transacciones de ESCRITURA en SAP Business One SL.
    Usa la API REST (Service Layer).
    """

    def __init__(self, request_user=None):
        self.base_url = settings.SAP_SL_BASE_URL
        country = get_current_country()
        self.request_user = request_user
        
        # 1. Determinar base de datos según país
        if country == 'PE':
            self.company_db = settings.SAP_SL_COMPANY_DB_PE
            self.series = getattr(settings, 'SAP_SL_SERIES_PE', 36)
        elif country == 'CO':
            self.company_db = settings.SAP_SL_COMPANY_DB_CO
            self.series = 36
        else:
            self.company_db = getattr(settings, 'SAP_SL_COMPANY_DB', 'TESTPOLIFUSION')
            self.series = -1

        # 2. Determinar credenciales
        if request_user and request_user.sap_user and request_user.sap_password:
            self.user = request_user.sap_user
            self.password = request_user.sap_password
            logger.info(f"SAP SL: Usando credenciales personalizadas de usuario para {request_user.username}")
        elif country == 'PE':
            self.user = settings.SAP_SL_USER_PE
            self.password = settings.SAP_SL_PASSWORD_PE
        elif country == 'CO':
            self.user = settings.SAP_SL_USER_CO
            self.password = settings.SAP_SL_PASSWORD_CO
        else:
            # Fallback explícito garantizado para Chile / General
            # Si getattr() devuelve string vacío, el "or" asegura el fallback a 'ccalidad'
            self.user = getattr(settings, 'SAP_SL_USER', 'ccalidad') or 'ccalidad'
            self.password = getattr(settings, 'SAP_SL_PASSWORD', 'Plf5647**') or 'Plf5647**'
            
        self.session_cookies = None
        self._executor = ThreadPoolExecutor(max_workers=5)

    def _get_cache_key(self):
        return f"sap_session_{self.company_db}_{self.user}"

    def _login(self):
        cache_key = self._get_cache_key()
        cached_cookies = cache.get(cache_key)
        
        if cached_cookies:
            self.session_cookies = cached_cookies
            return True

        url = f"{self.base_url}/Login"
        payload = {
            "CompanyDB": self.company_db,
            "UserName": self.user,
            "Password": self.password
        }
        
        try:
            logger.info(f"SAP SL: Logging in to {self.company_db}...")
            response = requests.post(url, json=payload, verify=False, timeout=10)
            
            if response.status_code == 200:
                self.session_cookies = response.cookies
                cache.set(cache_key, self.session_cookies, timeout=1200)
                return True
            else:
                logger.error(f"SAP SL: Login Failed ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            logger.exception(f"SAP SL: Login Exception: {e}")
            return False

    def run_async(self, func, *args, **kwargs):
        return self._executor.submit(func, *args, **kwargs)

    def create_service_call(self, customer_code, subject, description, priority='scp_Medium', 
                           technician_code=None, ship_address=None, bp_project_code=None, 
                           start_date=None, start_time=None, salesperson_code=None, 
                           salesperson_name=None, obra_name=None, problem_type=None,
                           category_name=None, subcategory_name=None, **kwargs):
        """
        Crea una Llamada de Servicio con soporte total para todos los parámetros del backend.
        Implementa bucle de resiliencia acumulativo para Perú, Chile y Colombia.
        """
        from apps.sap_integration.sap_query_service import SAPQueryService
        query_service = SAPQueryService()
        
        if not self.session_cookies:
            if not self._login():
                return {'success': False, 'error': 'SAP Auth Failed'}

        url = f"{self.base_url}/ServiceCalls"
        country = get_current_country()
        
        # 1. Preparación de técnicos
        final_tech_code = technician_code
        if final_tech_code and isinstance(final_tech_code, str) and not str(final_tech_code).isdigit():
            logger.info(f"SAP SL: Resolviendo técnico por nombre: {final_tech_code}")
            resolved_id = query_service.get_employee_id_by_name(final_tech_code)
            if resolved_id:
                final_tech_code = resolved_id

        if not final_tech_code:
            final_tech_code = query_service.get_fallback_technician_id()

        # 2. Construcción del Payload Inicial
        prio_map = {'scp_Low': 'scp_Low', 'scp_Medium': 'scp_Medium', 'scp_High': 'scp_High',
                    'baja': 'scp_Low', 'media': 'scp_Medium', 'alta': 'scp_High', 'critica': 'scp_High'}
        final_prio = prio_map.get(str(priority).lower(), 'scp_Medium')

        payload = {
            "CustomerCode": str(customer_code),
            "Subject": str(subject)[:99],
            "Description": str(description)[:1000] if description else "",
            "Priority": final_prio,
            "Status": 1 if country == 'PE' else -3,  # 1 = scOpen en PE
            "ServiceBPType": "srvcSales",
        }
        
        # 1. Configuración de Base (Series, Origin)
        if country == 'CL':
            # Chile se queda como está (sin Series ni Origin por ahora)
            pass
        elif country == 'CO':
            payload["Series"] = self.series # Usualmente -1
            payload["Origin"] = -1 # Web (según OSCO de TSTPOLCOLOMBIA_2)
        else:
            # Otros países (PE)
            payload["Series"] = self.series
            payload["Origin"] = 1
        
        # 2. Configuración de Roles (Assignee vs Technician)
        if country == 'PE':
            # En Perú, el Responsable del formulario mapea al 'Tratado por' (AssigneeCode)
            try:
                resp_id = None
                if final_tech_code:
                    try: resp_id = int(final_tech_code)
                    except: pass
                
                payload["AssigneeCode"] = resp_id if resp_id else 31
                payload["TechnicianCode"] = 1 # Luis Custodio
            except Exception as pe_err:
                logger.error(f"SAP SL PE: Error mapping roles: {pe_err}")
                payload["AssigneeCode"] = 31
                payload["TechnicianCode"] = 1
        elif country == 'CO':
            # En Colombia, el Responsable del formulario mapea al 'Tratado por' (AssigneeCode)
            try:
                resp_id = None
                if final_tech_code:
                    try: resp_id = int(final_tech_code)
                    except: pass
                
                payload["AssigneeCode"] = resp_id if resp_id else 22
                payload["TechnicianCode"] = 2 # Técnico (empID) predeterminado rastreado en OHEM
            except Exception as co_err:
                logger.error(f"SAP SL CO: Error mapping roles: {co_err}")
                payload["AssigneeCode"] = 2
                payload["TechnicianCode"] = 2
        else:
            # Lógica estándar (Chile)
            if final_tech_code:
                try: 
                    payload["TechnicianCode"] = int(final_tech_code)
                except: pass

        # 3. Vendedor (Solo vía UDF, SalesEmployee no existe en ServiceCalls de esta versión)
        # Se omite SalesEmployee/SalesPersonCode para evitar errores de propiedad inválida.

        # 4. ProblemType y CallType base por país
        if problem_type:
            payload["ProblemType"] = problem_type
        
        if country == 'CL':
            payload["ProblemType"] = 33
            payload["CallType"] = 1
        elif country == 'PE':
            payload["ProblemType"] = 13
            payload["CallType"] = 2
        elif country == 'CO':
            payload["ProblemType"] = 33
            payload["CallType"] = 1 # 'Post-Vent' (ID Confirmado en SAP)
        else:
            if not payload.get("ProblemType"): payload["ProblemType"] = 33
            payload["CallType"] = 1

        # 4. Campos de Obra / Proyecto
        if bp_project_code and country != 'CL':
            # Chile se omite para restaurar su estado previo 'perfecto'
            payload["BPProjectCode"] = bp_project_code
        
        if obra_name:
            payload["U_NX_NOM_PRO"] = str(obra_name)[:100]

        # 5. Vendedor (UDF)
        if country in ('CL', 'PE'):
            if salesperson_name:
                payload["U_NX_VENDEDOR"] = str(salesperson_name)[:50]
            elif country == 'PE':
                payload["U_NX_VENDEDOR"] = 'FABRICA'

        # Datos adicionales
        if ship_address: payload["BPShipToAddress"] = ship_address
        if start_date: payload["StartDate"] = str(start_date)
        if start_time: payload["StartTime"] = start_time

        # BUCLE DE REINTENTOS ACUMULATIVO
        max_retries = 3
        retry_count = 0
        last_error = ""
        
        logger.info(f"SAP SL {country}: Payload Final: {json.dumps(payload)}")

        try:
            while retry_count < max_retries:
                logger.info(f"SAP SL: Attempt {retry_count + 1} for {customer_code} | Project: {payload.get('BPProjectCode')}")
                response = requests.post(url, json=payload, cookies=self.session_cookies, verify=False, timeout=15)
                
                if response.status_code == 201:
                    data = response.json()
                    logger.info(f"SAP SL: Success on attempt {retry_count + 1}. DocNum: {data.get('DocNum')}")
                    return {
                        'success': True, 
                        'service_call_id': data.get('ServiceCallID'), 
                        'doc_num': data.get('DocNum'), 
                        'data': data
                    }
                
                if response.status_code == 401 and self._login():
                    retry_count += 1
                    continue

                # Analizar Error
                try:
                    error_data = response.json().get('error', {})
                    error_msg = str(error_data.get('message', {}).get('value', '')).lower()
                except:
                    error_msg = response.text.lower()
                
                last_error = error_msg
                logger.warning(f"SAP SL Trial {retry_count + 1} Failed for {customer_code}: {last_error}")

                # IDENTIFICAR Y APLICAR REPARACIONES
                repaired = False

                # A. Reparación de Técnico (-6101, -6103, oscl.technician, -2028)
                if any(x in last_error for x in ['technician', 'tecnico', 'técnico', '-6103', 'assignee', 'role', '10000673', '2028']):
                    logger.warning("SAP SL Repair: Cambiando técnico por falla de rol o posición.")
                    if country == 'PE':
                        if payload.get('AssigneeCode') != 31:
                            payload['AssigneeCode'] = 31 # Percy Luey
                            payload['TechnicianCode'] = 1 # Luis Custodio
                            payload['U_NX_VENDEDOR'] = 'FABRICA'
                            repaired = True
                        else:
                            payload.pop('AssigneeCode', None)
                            payload.pop('TechnicianCode', None)
                            repaired = True
                    else:
                        fallback_id = query_service.get_fallback_technician_id()
                        if fallback_id:
                            payload['AssigneeCode'] = fallback_id
                            payload['TechnicianCode'] = fallback_id
                            repaired = True
                        else:
                            payload.pop('AssigneeCode', None)
                            payload.pop('TechnicianCode', None)
                            repaired = True

                # B. Reparación de Obra/Proyecto (-6101, -2028)
                if any(x in last_error for x in ['project', 'obra', '6101', 'coincidencias', '2028']):
                    logger.warning("SAP SL Repair: Intentando corregir proyecto.")
                    projects = query_service.get_customer_projects(customer_code)
                    current_proj = payload.get('BPProjectCode')
                    if projects and str(projects[0].get('proyecto')) != str(current_proj):
                        payload['BPProjectCode'] = projects[0].get('proyecto')
                        repaired = True
                    else:
                        payload.pop('BPProjectCode', None)
                        payload.pop('U_NX_OBRA', None)
                        repaired = True

                # C. Reparación de Motivo/Tipo (-6102, -2028)
                if any(x in last_error for x in ['motivo', 'problem type', 'call type', '-6102', '2028']):
                    logger.warning("SAP SL Repair: Aplicando tipos base por país.")
                    if country == 'PE':
                        payload['ProblemType'] = 13
                        payload['CallType'] = 2
                    repaired = True

                # D. Limpieza de Series/Origin (-10, -2028)
                if not repaired and any(x in last_error for x in ['series', 'origin', '-10', '2028']):
                    payload.pop('Series', None)
                    payload.pop('Origin', None)
                    repaired = True

                if not repaired:
                    break
                
                retry_count += 1

            # Fallo final tras reintentos
            try:
                from apps.audit.models import AuditLog
                AuditLog.objects.create(
                    action='sap_sync_error',
                    description=f"Fallo persistente tras {retry_count + 1} intentos para {customer_code}. Error: {str(last_error)[:150]}",
                    details={'error': str(last_error), 'payload': payload}
                )
            except: pass
            
            return {'success': False, 'error': f"SAP SL Final Failure: {last_error}"}

        except Exception as e:
            logger.exception(f"Critical error in create_service_call: {e}")
            return {'success': False, 'error': str(e)}

    def update_service_call(self, call_id, update_data):
        if not self.session_cookies and not self._login(): return {'success': False, 'error': 'Auth Failed'}
        url = f"{self.base_url}/ServiceCalls({call_id})"
        try:
            response = requests.patch(url, json=update_data, cookies=self.session_cookies, verify=False, timeout=30)
            if response.status_code == 204: return {'success': True}
            return {'success': False, 'error': response.text}
        except Exception as e: return {'success': False, 'error': str(e)}

    def close_service_call(self, call_id, resolution, visit_date=None, technician_code=None):
        payload = {"Status": -1, "Resolution": resolution or "Cerrada desde Postventa."}
        if visit_date: payload["U_NX_FECHAVISITA"] = visit_date
        if technician_code:
            try: payload["TechnicianCode"] = int(technician_code)
            except: pass
        return self.update_service_call(call_id, payload)

    def cancel_service_call(self, call_id, resolution=None):
        """
        Cancela una Llamada de Servicio en SAP. 
        En este sistema específico, el ID 1 corresponde al estado 'Cancelada'.
        """
        # Usamos Status 1 para 'Cancelada' según requerimiento del usuario (Chile).
        payload = {"Status": 1}
        
        if resolution:
            # Asegurar mensaje limpio (ASCII) para evitar rechazos parciales de SAP
            import unicodedata
            clean_res = unicodedata.normalize('NFKD', str(resolution)).encode('ascii', 'ignore').decode('ascii')
            payload["Resolution"] = clean_res
        else:
            payload["Resolution"] = "Cancelada desde la App Postventa."

        logger.info(f"[SAP-TX] Cancelando SC {call_id}. Payload: {payload}")
        return self.update_service_call(call_id, payload)

    def get_technicians(self):
        if not self.session_cookies and not self._login(): return []
        url = f"{self.base_url}/EmployeesInfo?$select=EmployeeID,FirstName,LastName,eMail&$filter=Active eq 'tYES'&$orderby=FirstName,LastName"
        try:
            res = requests.get(url, cookies=self.session_cookies, verify=False, timeout=15)
            if res.status_code == 200:
                return [{'id': r.get('EmployeeID'), 'name': f"{r.get('FirstName','')} {r.get('LastName','')}".strip()} for r in res.json().get('value', [])]
        except: pass
        return []

    def logout(self):
        if self.session_cookies:
            try: requests.post(f"{self.base_url}/Logout", cookies=self.session_cookies, verify=False)
            except: pass
            self.session_cookies = None

    def upload_attachment_to_service_call(self, call_id, file_path, filename, replace_if_exists=True):
        """
        Sube un archivo a SAP. Si la llamada ya tiene adjuntos, los concatena usando PATCH.
        """
        if not self.session_cookies and not self._login(): 
            return {'success': False, 'error': 'Auth Failed'}

        # 1. Asegurar nombre único para evitar error SAP: "A file with this name already exists"
        unique_filename = f"SC{call_id}_{filename}"
        
        # 2. Bloqueo por Service Call para evitar condiciones de carrera en subidas concurrentes
        lock_dir = os.path.join(settings.BASE_DIR, 'tmp')
        if not os.path.exists(lock_dir):
            os.makedirs(lock_dir, exist_ok=True)
            
        lock_path = os.path.join(lock_dir, f"sap_atc_{call_id}.lock")
        lock = FileLock(lock_path, timeout=120)

        try:
            with lock:
                # 3. Verificar si ya existe un AttachmentEntry vinculado
                atc_entry = None
                sc_url = f"{self.base_url}/ServiceCalls({call_id})"
                sc_res = requests.get(sc_url, cookies=self.session_cookies, verify=False, timeout=15)
                
                if sc_res.status_code == 200:
                    atc_entry = sc_res.json().get('AttachmentEntry')
                
                # 4. Subir el archivo
                if atc_entry:
                    # Caso APPEND: PATCH al actual
                    url = f"{self.base_url}/Attachments2({atc_entry})"
                    method = requests.patch
                    success_codes = (200, 204)
                    logger.info(f"SAP SL: Anexando {unique_filename} al AttachmentEntry {atc_entry} existente.")
                else:
                    # Caso NUEVO: POST inicial
                    url = f"{self.base_url}/Attachments2"
                    method = requests.post
                    success_codes = (200, 201)
                    logger.info(f"SAP SL: Creando nuevo AttachmentEntry para {unique_filename}.")

                with open(file_path, 'rb') as f:
                    files = {'files': (unique_filename, f, 'application/octet-stream')}
                    response = method(url, files=files, cookies=self.session_cookies, verify=False, timeout=60)
                
                if response.status_code not in success_codes:
                    logger.error(f"SAP SL: Error subiendo {unique_filename}. Status: {response.status_code}, Res: {response.text}")
                    return {'success': False, 'error': f"Attachment {method.__name__} failed: {response.text}"}
                
                # Si fue un POST nuevo, vincularlo a la Service Call
                if not atc_entry:
                    new_atc_entry = response.json().get('AbsoluteEntry')
                    if not new_atc_entry:
                        return {'success': False, 'error': 'No AbsoluteEntry in SAP response'}
                    
                    res = self.update_service_call(call_id, {"AttachmentEntry": new_atc_entry})
                    if res.get('success'):
                        logger.info(f"SAP SL: Nuevo AttachmentEntry {new_atc_entry} vinculado a SC {call_id}")
                        return {'success': True, 'atc_entry': new_atc_entry}
                    return res
                else:
                    return {'success': True, 'atc_entry': atc_entry, 'mode': 'appended'}

        except Exception as e:
            logger.exception(f"Error subiendo adjunto a SAP (SC {call_id}): {e}")
            return {'success': False, 'error': str(e)}

    def update_service_call_from_visit_report(self, report):
        """
        Sincroniza UDFs y datos maestros de un VisitReport con SAP.
        """
        from apps.sap_integration.sap_query_service import SAPQueryService
        query_service = SAPQueryService()
        
        # DocNum -> CallID si es necesario
        call_id = report.sap_call_id
        if not call_id: return {'success': False, 'error': 'No SAP ID in report'}

        # Mapeo de UDFs (Observaciones y Metadatos)
        payload = {
            "U_NX_OBS_MURO": str(report.wall_observations or "")[:254],
            "U_NX_OBS_MATRIZ": str(report.matrix_observations or "")[:254],
            "U_NX_OBS_LOSA": str(report.slab_observations or "")[:254],
            "U_NX_OBS_ALMAC": str(report.storage_observations or "")[:254],
            "U_NX_OBS_PRE_ARM": str(report.pre_assembled_observations or "")[:254],
            "U_NX_OBS_EXTER": str(report.exterior_observations or "")[:254],
            "U_NX_GENE": str(report.general_observations or "")[:254],
            "U_NX_FECHAVISITA": report.visit_date.strftime('%Y-%m-%d') if report.visit_date else None,
        }

        # Datos de Máquinas
        m_data = report.machine_data or {}
        if m_data.get('machine_removal'): payload["U_NX_RET_MQ"] = 1
        
        machines = m_data.get('machines', [])
        for i, m in enumerate(machines[:6]):
            idx = i + 1
            if m.get('machine'): payload[f"U_NX_MAQ{idx}"] = str(m['machine'])[:100]
            if m.get('start'): payload[f"U_NX_INI{idx}"] = m['start']
            if m.get('cut'): payload[f"U_NX_COR{idx}"] = m['cut']

        # Limpiar valores None
        payload = {k: v for k, v in payload.items() if v is not None}
        
        logger.info(f"SAP SL: Actualizando UDFs para CallID {call_id}")
        return self.update_service_call(call_id, payload)
