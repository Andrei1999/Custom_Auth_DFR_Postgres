from django.urls import path

from .views import InvoiceListView, ProjectListCreateView, ReportListGenerateView

urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='mock-projects'),
    path('reports/', ReportListGenerateView.as_view(), name='mock-reports'),
    path('invoices/', InvoiceListView.as_view(), name='mock-invoices'),
]
