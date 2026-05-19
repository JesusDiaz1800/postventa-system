from django.urls import path
from .views import VisitReportListView, VisitReportDetailView
from . import views


urlpatterns = [
    path('', VisitReportListView.as_view(), name='visit-reports-list'),
    path('<int:pk>/', VisitReportDetailView.as_view(), name='visit-reports-detail'),
    path('<int:pk>/pdf/', views.generate_visit_pdf, name='visit-report-pdf'),
    path('<int:pk>/send-email/', views.send_visit_report_email, name='visit-report-email'),

]
