from django.db import models

class BusinessPartner(models.Model):
    """
    Tabla maestra de socios de negocios (Clientes)
    SAP Table: OCRD
    """
    card_code = models.CharField(db_column='CardCode', primary_key=True, max_length=15)
    card_name = models.CharField(db_column='CardName', max_length=100, blank=True, null=True)
    card_type = models.CharField(db_column='CardType', max_length=1)  # C=Customer, S=Supplier, L=Lead
    email_address = models.CharField(db_column='E_Mail', max_length=100, blank=True, null=True)
    phone1 = models.CharField(db_column='Phone1', max_length=20, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'OCRD'
        verbose_name = 'Socio de Negocio'
        verbose_name_plural = 'Socios de Negocio'

class ServiceCall(models.Model):
    call_id = models.IntegerField(db_column='callID', primary_key=True)
    doc_num = models.IntegerField(db_column='DocNum', blank=True, null=True)
    subject = models.CharField(db_column='subject', max_length=200, blank=True, null=True)
    customer_code = models.CharField(db_column='customer', max_length=15, blank=True, null=True)
    customer_name = models.CharField(db_column='custmrName', max_length=100, blank=True, null=True)
    status = models.IntegerField(db_column='status', blank=True, null=True)
    create_date = models.DateTimeField(db_column='createDate', blank=True, null=True)
    create_time_raw = models.SmallIntegerField(db_column='createTime', blank=True, null=True)  # Minutos desde 00:00
    priority_raw = models.SmallIntegerField(db_column='priority', blank=True, null=True)  # 0=Low, 1=Medium, 2=High
    
    # Nuevos Campos Estándar
    update_date = models.DateTimeField(db_column='updateDate', blank=True, null=True)
    close_date = models.DateTimeField(db_column='closeDate', blank=True, null=True)
    technician = models.CharField(db_column='technician', max_length=50, blank=True, null=True)
    description = models.TextField(db_column='descrption', blank=True, null=True) # Typo SAP
    contact_code = models.IntegerField(db_column='contctCode', blank=True, null=True)
    assignee = models.SmallIntegerField(db_column='assignee', blank=True, null=True) # Código empleado asignado
    
    
    
    # Datos de Contacto y Ubicacion
    telephone = models.CharField(db_column='Telephone', max_length=50, blank=True, null=True)
    bp_ship_addr = models.CharField(db_column='BPShipAddr', max_length=250, blank=True, null=True)
    ship_street = models.CharField(db_column='Street', max_length=150, blank=True, null=True)
    ship_city = models.CharField(db_column='City', max_length=100, blank=True, null=True)
    # ship_county = models.CharField(db_column='County', max_length=100, blank=True, null=True)
    
    # Motivo de servicio
    problem_type = models.CharField(db_column='problemTyp', max_length=50, blank=True, null=True)

    # CAMPOS PERSONALIZADOS (UDFs)
    bp_project_code = models.CharField(db_column='BPProjCode', max_length=50, blank=True, null=True)
    project_name_udf = models.CharField(db_column='U_NX_NOM_PRO', max_length=100, blank=True, null=True)
    salesperson_name = models.CharField(db_column='U_NX_VENDEDOR', max_length=50, blank=True, null=True)
    mezclado_int = models.SmallIntegerField(db_column='U_NX_MEZCLADO', blank=True, null=True)
    
    # Observaciones Específicas
    obs_general = models.TextField(db_column='U_NX_GENE', blank=True, null=True)
    obs_muro = models.TextField(db_column='U_NX_OBS_MURO', blank=True, null=True)
    obs_matriz = models.TextField(db_column='U_NX_OBS_MATRIZ', blank=True, null=True)
    obs_losa = models.TextField(db_column='U_NX_OBS_LOSA', blank=True, null=True)
    obs_almac = models.TextField(db_column='U_NX_OBS_ALMAC', blank=True, null=True)
    obs_pre_arm = models.TextField(db_column='U_NX_OBS_PRE_ARM', blank=True, null=True)
    obs_exter = models.TextField(db_column='U_NX_OBS_EXTER', blank=True, null=True)
    
    # Datos de Máquinas
    maq1 = models.CharField(db_column='U_NX_MAQ1', max_length=100, blank=True, null=True)
    ini1 = models.CharField(db_column='U_NX_INI1', max_length=100, blank=True, null=True)
    cor1 = models.CharField(db_column='U_NX_COR1', max_length=100, blank=True, null=True)
    maq2 = models.CharField(db_column='U_NX_MAQ2', max_length=100, blank=True, null=True)
    ini2 = models.CharField(db_column='U_NX_INI2', max_length=100, blank=True, null=True)
    cor2 = models.CharField(db_column='U_NX_COR2', max_length=100, blank=True, null=True)
    maq3 = models.CharField(db_column='U_NX_MAQ3', max_length=100, blank=True, null=True)
    ini3 = models.CharField(db_column='U_NX_INI3', max_length=100, blank=True, null=True)
    cor3 = models.CharField(db_column='U_NX_COR3', max_length=100, blank=True, null=True)
    maq4 = models.CharField(db_column='U_NX_MAQ4', max_length=100, blank=True, null=True)
    ini4 = models.CharField(db_column='U_NX_INI4', max_length=100, blank=True, null=True)
    cor4 = models.CharField(db_column='U_NX_COR4', max_length=100, blank=True, null=True)
    maq5 = models.CharField(db_column='U_NX_MAQ5', max_length=100, blank=True, null=True)
    ini5 = models.CharField(db_column='U_NX_INI5', max_length=100, blank=True, null=True)
    cor5 = models.CharField(db_column='U_NX_COR5', max_length=100, blank=True, null=True)
    maq6 = models.CharField(db_column='U_NX_MAQ6', max_length=100, blank=True, null=True)
    ini6 = models.CharField(db_column='U_NX_INI6', max_length=100, blank=True, null=True)
    cor6 = models.CharField(db_column='U_NX_COR6', max_length=100, blank=True, null=True)
    retiro_maq = models.SmallIntegerField(db_column='U_NX_RET_MQ', blank=True, null=True)
    nro_reporte = models.IntegerField(db_column='U_NX_NREPORT', blank=True, null=True)
    
    # UDFs Complementarios Identificados (Reporte / Traslado)
    obra_rescatada = models.SmallIntegerField(db_column='U_NX_RESCATADA', blank=True, null=True)
    patente = models.CharField(db_column='U_NX_PATENTE', max_length=100, blank=True, null=True)
    obra_finalizada = models.SmallIntegerField(db_column='U_NX_OBRAFINALIZADA', blank=True, null=True)
    fecha_visita_udf = models.DateTimeField(db_column='U_NX_FECHAVISITA', blank=True, null=True)
    obs_critica = models.CharField(db_column='U_obs_critica', max_length=250, blank=True, null=True)
    obra_otro_proveedor = models.CharField(db_column='U_obra_con_otro_proveedor', max_length=50, blank=True, null=True)
    nivel_instalacion = models.CharField(db_column='U_nivel_instalacion', max_length=100, blank=True, null=True)
    otro_proveedor = models.CharField(db_column='U_otro_proveedor', max_length=100, blank=True, null=True)
    
    # UDFs de Clasificación (App ↔ SAP)
    sap_category_udf = models.CharField(db_column='U_is_categoria', max_length=100, blank=True, null=True)
    sap_subcategory_udf = models.CharField(db_column='U_is_subcategoria', max_length=100, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'OSCL'
        verbose_name = 'Llamada de Servicio'
        verbose_name_plural = 'Llamadas de Servicio'

class Project(models.Model):
    """
    Tabla de obras (User Defined Table)
    SAP Table: @FRMOBRAS
    """
    code = models.CharField(db_column='Code', primary_key=True, max_length=50)
    name = models.CharField(db_column='Name', max_length=100, blank=True, null=True)
    card_code = models.CharField(db_column='U_nx_cardcode', max_length=15, blank=True, null=True)
    
    # Campos personalizados para Reporte (Direccion, Instalador, Etc)
    address = models.CharField(db_column='U_nx_direccion', max_length=200, blank=True, null=True)
    commune = models.CharField(db_column='U_nx_comuna', max_length=100, blank=True, null=True)
    city = models.CharField(db_column='U_nx_ciudad', max_length=100, blank=True, null=True)
    
    installer_name = models.CharField(db_column='U_nx_inst_nom', max_length=100, blank=True, null=True)
    installer_phone = models.CharField(db_column='U_nx_fono_inst', max_length=50, blank=True, null=True)
    
    construction_company = models.CharField(db_column='U_nx_construc', max_length=100, blank=True, null=True)
    admin_name = models.CharField(db_column='U_nx_administrador', max_length=100, blank=True, null=True)
    
    # Otros posibles contactos
    prof_obra_nom = models.CharField(db_column='U_prof_obra_nom', max_length=100, blank=True, null=True)
    ito_nom = models.CharField(db_column='U_ito_nom', max_length=100, blank=True, null=True)
    otros_nom = models.CharField(db_column='U_otros_nom', max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '@FRMOBRAS'
        verbose_name = 'Obra'
        verbose_name_plural = 'Obras'
