from django.urls import path
from . import views

urlpatterns = [
    # Búsqueda de clientes
    path('customers/search/', views.search_sap_customers, name='sap-customers-search'),
    path('customers/<str:card_code>/', views.get_sap_customer, name='sap-customer-detail'),
    path('customers/<str:card_code>/projects/', views.get_customer_projects, name='sap-customer-projects'),
    path('customer-details/<str:card_code>/', views.get_customer_details, name='sap-customer-full-details'),
    path('sales-employees/', views.get_sales_employees, name='sap-sales-employees'),
    path('technicians/', views.get_technicians, name='sap-technicians'),
    
    # Llamadas de servicio
    path('service-calls/recent/', views.get_recent_service_calls, name='sap-recent-calls'),
    path('service-calls/<int:doc_num>/', views.get_sap_service_call, name='sap-service-call-detail'),
    
    # Adjuntos (Attachments)
    path('attachments/<int:atc_entry>/<int:line>/', views.download_sap_attachment, name='sap-attachment-download'),
]
