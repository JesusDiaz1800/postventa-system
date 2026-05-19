import requests
import logging
import json
import time
import os
import base64
from datetime import datetime
from filelock import FileLock
from django.conf import settings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor
import threading
from apps.core.thread_local import get_current_country
from django.db import connections

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class SAPTransactionService:
    """
    Servicio Premium para transacciones de ESCRITURA en SAP Business One SL.
    Soporta multi-tenant (CL, CO, PE), mapeo de UDFs masivo y Anexos.
    """

    def __init__(self, request_user=None):
        self.base_url = settings.SAP_SL_BASE_URL
        self.request_user = request_user
        
        # 1. Determinar el país (Tenant)
        if request_user:
            self.country = request_user.country_code
        else:
            self.country = get_current_country()

        # 2. Determinar base de datos según país
        if self.country == 'PE':
            self.company_db = settings.SAP_SL_COMPANY_DB_PE
            self.series = getattr(settings, 'SAP_SL_SERIES_PE', 36)
        elif self.country == 'CO':
            self.company_db = settings.SAP_SL_COMPANY_DB_CO
            self.series = 36
        else:
            self.company_db = getattr(settings, 'SAP_SL_COMPANY_DB', 'TESTPOLIFUSION')
            self.series = 36 # Series 36 es estándar para Polifusión

        # 3. Credenciales Inteligentes (User -> Fallback Country)
        if request_user and request_user.sap_user and request_user.sap_password:
            self.user = request_user.sap_user
            self.password = request_user.sap_password
        elif self.country == 'PE':
            self.user = settings.SAP_SL_USER_PE
            self.password = settings.SAP_SL_PASS_PE
        elif self.country == 'CO':
            self.user = settings.SAP_SL_USER_CO
            self.password = settings.SAP_SL_PASS_CO
        else:
            self.user = settings.SAP_SL_USER_CL
            self.password = settings.SAP_SL_PASS_CL
            
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
            logger.info(f"SAP SL: Login to {self.company_db} ({self.user})...")
            response = requests.post(url, json=payload, verify=False, timeout=15)
            
            if response.status_code == 200:
                self.session_cookies = response.cookies
                cache.set(cache_key, self.session_cookies, timeout=1800)
                return True
            else:
                logger.error(f"SAP SL Login Error ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            logger.error(f"SAP SL Exception during login: {e}")
            return False

    def upload_attachments(self, files):
        """
        Sube archivos al Service Layer y devuelve el AbsEntry (AttachmentEntry).
        files: lista de diccionarios [{'name': 'foto.jpg', 'content': b64_string}, ...]
        """
        if not self.session_cookies and not self._login():
            return None

        url = f"{self.base_url}/Attachments2"
        
        # El Service Layer requiere multipart/form-data para anexos
        # Pero podemos usar un endpoint específico o la API de archivos según versión
        # Aquí implementamos la lógica base de adjuntos
        try:
            # Nota: Algunos SL requieren subir vía Boundary o Binary
            # Implementamos la versión más compatible:
            boundary = '----SAPBoundary'
            headers = {
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Connection': 'keep-alive'
            }
            
            body = []
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            for f in files:
                original_name = f.get('name')
                # Hacer el nombre único para evitar error -10 de SAP
                name_parts = original_name.rsplit('.', 1)
                if len(name_parts) > 1:
                    filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    filename = f"{original_name}_{timestamp}"
                
                content = base64.b64decode(f.get('content')) if isinstance(f.get('content'), str) else f.get('content')
                
                body.append(f'--{boundary}')
                body.append(f'Content-Disposition: form-data; name="files"; filename="{filename}"')
                body.append('Content-Type: application/octet-stream')
                body.append('')
                body.append(content)
                
            body.append(f'--{boundary}--')
            body.append('')
            
            # Unir el cuerpo (asegurar bytes)
            full_body = b''
            for part in body:
                if isinstance(part, str):
                    full_body += part.encode('utf-8') + b'\r\n'
                else:
                    full_body += part + b'\r\n'

            response = requests.post(url, data=full_body, headers=headers, cookies=self.session_cookies, verify=False, timeout=30)
            
            if response.status_code in (200, 201):
                return response.json().get('AbsoluteEntry')
            else:
                logger.error(f"SAP SL Attachment Error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception during attachment upload: {e}")
            return None

    def create_service_call(self, customer_code, subject, description, technician_code=None, 
                            obra_name=None, bp_project_code=None, udf_data=None, **kwargs):
        """
        Crea una Llamada de Servicio con mapeo completo de UDFs y Anexos.
        """
        if not self.session_cookies and not self._login():
            return {'success': False, 'error': 'Auth Failure'}

        url = f"{self.base_url}/ServiceCalls"
        udf_data = udf_data or {}
        
        # 1. Construcción del Payload Base
        payload = {
            "CustomerCode": str(customer_code),
            "Subject": str(subject)[:99],
            "Description": str(description)[:1000] if description else "",
            "Priority": "scp_Medium",
            "Status": 1 if self.country == 'PE' else -3,
            "ServiceBPType": "srvcSales",
            "BPProjectCode": str(bp_project_code) if bp_project_code else None,
            "Series": self.series
        }

        # 2. Determinar alias de BD SAP para consultas
        db_map = {'CL': 'sap_db', 'PE': 'sap_db_pe', 'CO': 'sap_db_co'}
        sap_db = db_map.get(self.country, 'sap_db')

        # 2.1 Técnico
        tech_id = int(technician_code) if technician_code else 1
        payload["TechnicianCode"] = tech_id

        # 2.2 AssigneeCode: El "Tratado Por" siempre será el usuario de jefatura técnica (ccalidad)
        assignee_id = tech_id  # Fallback inicial
        sap_user = 'ccalidad'
        try:
            with connections[sap_db].cursor() as c:
                # Buscamos el empID en OHEM vinculado al USER_CODE de OUSR
                query = """
                    SELECT T1.empID 
                    FROM OUSR T0 
                    INNER JOIN OHEM T1 ON T0.USERID = T1.userId 
                    WHERE UPPER(T0.USER_CODE) = UPPER(%s)
                """
                c.execute(query, [sap_user])
                row = c.fetchone()
                if row:
                    assignee_id = row[0]
                    logger.info(f"AssigneeCode (OHEM empID) resuelto: {assignee_id} para usuario {sap_user}")
                else:
                    # Fallback: buscar solo en OUSR por si no tiene empleado vinculado
                    c.execute("SELECT USERID FROM OUSR WHERE UPPER(USER_CODE) = UPPER(%s)", [sap_user])
                    row = c.fetchone()
                    if row:
                        assignee_id = row[0]
                        logger.info(f"AssigneeCode (OUSR USERID) resuelto: {assignee_id} para usuario {sap_user}")
        except Exception as e:
            logger.warning(f"Error resolviendo AssigneeCode: {e}")
            
        payload["AssigneeCode"] = assignee_id

        # 3. Clasificación por País
        payload["ProblemType"] = 1
        # Visita Técnica es 2 en Chile según captura del usuario
        payload["CallType"] = 2 if self.country == 'CL' else (2 if self.country == 'PE' else 1)

        # 4. MAPEO COMPLETO DE UDFs
        report_id_raw = kwargs.get('report_id', '')
        report_numeric_id = ''.join(filter(str.isdigit, str(report_id_raw))) or "0"

        # Fecha de visita formateada
        visit_date_raw = udf_data.get('visit_date', '')
        visit_date_str = ''
        if visit_date_raw:
            try:
                from datetime import datetime as dt
                visit_date_str = dt.fromisoformat(str(visit_date_raw)).strftime('%Y%m%d')
            except:
                visit_date_str = str(visit_date_raw)[:8]

        payload.update({
            # Identificación del reporte
            "U_NX_NOM_PRO":               str(obra_name or '')[:100],
            "U_NX_IDVISITA":              int(report_numeric_id),   # Era U_NX_NREPORT
            "U_NX_FECHAVISITA":           visit_date_str,
            # Vendedor (UDF texto, no campo nativo)
            "U_NX_VENDEDOR":              str(udf_data.get('salesperson_name', '') or '')[:100],
            # Observaciones técnicas
            "U_NX_OBS_MURO":              str(udf_data.get('obs_muro',    '') or '')[:250],
            "U_NX_OBS_MATRIZ":            str(udf_data.get('obs_matriz',  '') or '')[:250],
            "U_NX_OBS_LOSA":              str(udf_data.get('obs_losa',    '') or '')[:250],
            "U_NX_OBS_ALMAC":             str(udf_data.get('obs_almac',   '') or '')[:250],
            "U_NX_OBS_PRE_ARM":           str(udf_data.get('obs_pre_arm', '') or '')[:250],
            "U_NX_OBS_EXTER":             str(udf_data.get('obs_exter',   '') or '')[:250],
            "U_NX_GENE":                  str(description or '')[:250],
            "U_obs_critica":              str(udf_data.get('obs_critica', '') or '')[:250],  # Solo SAP, nunca en PDF

            # Métricas de obra (nombres exactos de CUFD y tipos verificados)
            "U_NX_MEZCLADO":              1 if udf_data.get('is_mixed_material') else 0,
            "U_NX_RESCATADA":             1 if udf_data.get('is_rescued_project') else 0,
            "U_NX_OBRAFINALIZADA":        1 if udf_data.get('is_project_finished') else 0,
            "U_NX_PATENTE":               str(udf_data.get('patent_number', '') or '')[:30],
            # Mapeo de Nivel de Instalación a Códigos SAP (Soporta ID numérico del form o Texto)
            "U_nivel_instalacion": str(udf_data.get('installation_level', '0')) if str(udf_data.get('installation_level', '')).isdigit() else {
                'NORMAL': '0',
                'DEFICIENTE': '1',
                'CRITICO': '2',
                'INEXISTENTE': '3',
                'NO_APLICA': '4'
            }.get(udf_data.get('installation_level', 'NORMAL'), '0'),

            "U_obra_con_otro_proveedor":  "1" if udf_data.get('is_other_provider') else "0",
            "U_otro_proveedor":           str(udf_data.get('other_provider_name', '') or '')[:30],
        })

        # 5. Mapeo de Máquinas (nombres verificados: NX_MAQ1..6, NX_INI1..6, NX_COR1..6)
        for i in range(1, 7):
            maq = udf_data.get(f'maq{i}', '')
            ini = udf_data.get(f'ini{i}', '')
            cor = udf_data.get(f'cor{i}', '')
            payload[f"U_NX_MAQ{i}"] = str(maq) if maq else ""
            payload[f"U_NX_INI{i}"] = str(ini) if ini and str(ini) not in ('0', '0.0') else ""
            payload[f"U_NX_COR{i}"] = str(cor) if cor and str(cor) not in ('0', '0.0') else ""

        # 6. Anexos
        attachments = kwargs.get('attachments', [])
        if attachments:
            atc_entry = self.upload_attachments(attachments)
            if atc_entry:
                payload["AttachmentEntry"] = atc_entry

        # BUCLE DE REINTENTOS
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                headers = {'B1S-ReplaceCollectionsOnPatch': 'true', 'Connection': 'keep-alive'}
                response = requests.post(url, json=payload, cookies=self.session_cookies, verify=False, timeout=25, headers=headers)
                
                if response.status_code in (200, 201):
                    data = response.json()
                    return {'success': True, 'doc_num': data.get('DocNum'), 'id': data.get('ServiceCallID')}
                
                # Auto-Reparación si falla por Técnico/Obra
                err_msg = response.text.lower()
                if any(x in err_msg for x in ['technician', 'employee', 'project', 'obra', '2028']):
                    logger.warning(f"SAP SL Repairing: {err_msg}")
                    if 'project' in err_msg or 'obra' in err_msg:
                        payload.pop('BPProjectCode', None)
                    else:
                        # Fallback técnico
                        payload['TechnicianCode'] = 1
                        payload['AssigneeCode'] = 1
                    retry_count += 1
                    continue
                
                return {'success': False, 'error': response.text}
            except Exception as e:
                logger.error(f"SAP SL Request Error: {e}")
                retry_count += 1
                
        return {'success': False, 'error': 'Max retries reached'}
    def update_service_call_attachment(self, service_call_id, files):
        """
        Sincroniza un anexo (ej: PDF firmado) con una llamada de servicio EXISTENTE.
        """
        if not self.session_cookies and not self._login():
            return {'success': False, 'error': 'Auth Failure'}

        # 1. Subir el archivo
        atc_entry = self.upload_attachments(files)
        if not atc_entry:
            return {'success': False, 'error': 'Failed to upload attachment'}

        # 2. Vincular a la llamada de servicio vía PATCH
        url = f"{self.base_url}/ServiceCalls({service_call_id})"
        payload = {"AttachmentEntry": atc_entry}
        
        try:
            response = requests.patch(url, json=payload, cookies=self.session_cookies, verify=False, timeout=20)
            if response.status_code in (200, 204):
                return {'success': True, 'atc_entry': atc_entry}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            logger.error(f"Error linking attachment to service call {service_call_id}: {e}")
            return {'success': False, 'error': str(e)}

    def close_service_call(self, service_call_id, resolution_text):
        """
        Cierra una Llamada de Servicio en SAP SL y añade la resolución.
        """
        if not self.session_cookies and not self._login():
            return {'success': False, 'error': 'Auth Failure'}

        url = f"{self.base_url}/ServiceCalls({service_call_id})"
        payload = {
            "Status": -1,
            "Resolution": str(resolution_text)[:1000]
        }
        
        try:
            logger.info(f"SAP SL: Cerrando Llamada de Servicio {service_call_id} con resolución")
            response = requests.patch(url, json=payload, cookies=self.session_cookies, verify=False, timeout=20)
            if response.status_code in (200, 204):
                return {'success': True}
            else:
                logger.error(f"Error al cerrar llamada en SAP ({response.status_code}): {response.text}")
                return {'success': False, 'error': response.text}
        except Exception as e:
            logger.error(f"Exception closing service call {service_call_id}: {e}")
            return {'success': False, 'error': str(e)}
