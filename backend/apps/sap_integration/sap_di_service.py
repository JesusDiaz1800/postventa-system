import pythoncom
import win32com.client
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Configuración Hardcoded (Temporal - Mover a .env luego)
# TODO: Move to settings/env
SAP_SERVER = "PLFSCL0VIR010"
SAP_COMPANY_DB = "PRDPOLIFUSION"
SAP_USER = "ccalidad"
SAP_PASSWORD = "Plf5647**"
DST_MSSQL2017 = 10

class SAPDIService:
    """
    Servicio para interactuar con SAP Business One DI API (COM).
    Permite escritura de transacciones (Service Calls, Activities, etc.).
    
    NOTA: COM es sensible a hilos. Cada método debe manejar su propia inicialización
    o ejecutarse en un proceso dedicado (Celery).
    """
    
    def __init__(self):
        self.company = None
        self.connected = False

    def connect(self):
        """Inicializa la conexión a la compañía"""
        try:
            # Inicializar COM en este hilo
            pythoncom.CoInitialize()
            
            self.company = win32com.client.Dispatch("SAPbobsCOM.Company")
            
            self.company.Server = SAP_SERVER
            self.company.CompanyDB = SAP_COMPANY_DB
            self.company.UserName = SAP_USER
            self.company.Password = SAP_PASSWORD
            self.company.DbServerType = DST_MSSQL2017
            self.company.UseTrusted = True # Windows Auth para SQL
            
            logger.info(f"Connecting to SAP DI API: {SAP_SERVER} / {SAP_COMPANY_DB}")
            
            ret = self.company.Connect()
            
            if ret == 0:
                self.connected = True
                logger.info("SAP DI API Connected Successfully")
                return True
            else:
                err_code, err_msg = self.company.GetLastError()
                logger.error(f"SAP Connection Failed: {err_code} - {err_msg}")
                self.connected = False
                return False
                
        except Exception as e:
            logger.error(f"SAP DI API Exception: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Cierra la conexión y libera recursos COM"""
        if self.company and self.connected:
            self.company.Disconnect()
            self.connected = False
            logger.info("SAP DI API Disconnected")
        
        # Liberar memoria COM
        self.company = None
        pythoncom.CoUninitialize()

    def create_service_call(self, customer_code, subject, description, priority='L', origin=-1):
        """
        Crea una Llamada de Servicio en SAP.
        
        Args:
            customer_code (str): CardCode del cliente.
            subject (str): Asunto (max 100 chars).
            description (str): Descripción detallada.
            priority (str): 'L', 'M', 'H'.
            origin (int): Origin ID (e.g., -1 for Web, or custom ID).
            
        Returns:
            dict: {success: bool, service_call_id: int, error: str}
        """
        if not self.connect():
            return {'success': False, 'error': 'Could not connect to SAP DI API'}

        service_call = None
        try:
            # Instanciar objeto ServiceCall (191)
            # oServiceCalls = 191
            service_call = self.company.GetBusinessObject(191)
            
            service_call.CustomerCode = customer_code
            service_call.Subject = subject[:99] # Truncate to fit
            service_call.Description = description
            
            # Mapeo de Prioridades
            prio_enum = 0 # Low
            if priority == 'M': prio_enum = 1
            if priority == 'H': prio_enum = 2
            service_call.Priority = prio_enum
            
            # service_call.Origin = origin # Opcional
            
            # Intentar agregar
            ret = service_call.Add()
            
            if ret == 0:
                # Éxito
                new_key = self.company.GetNewObjectKey()
                logger.info(f"Service Call Created! Key: {new_key}")
                return {'success': True, 'service_call_id': new_key}
            else:
                # Fallo
                err_code, err_msg = self.company.GetLastError()
                logger.error(f"Error creating Service Call: {err_code} - {err_msg}")
                return {'success': False, 'error': f"{err_code} - {err_msg}"}
                
        except Exception as e:
            logger.exception("Exception creating Service Call")
            return {'success': False, 'error': str(e)}
        finally:
            # Liberar objeto de negocio
            del service_call
            self.disconnect()

