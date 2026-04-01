from rest_framework.response import Response
from rest_framework.views import APIView


class ProjectListCreateView(APIView):
    required_permissions = {
        'GET': ('projects', 'read'),
        'POST': ('projects', 'create'),
    }

    def get(self, request):
        data = [
            {'id': 1, 'name': 'CRM upgrade', 'status': 'active'},
            {'id': 2, 'name': 'Internal portal', 'status': 'draft'},
        ]
        return Response(data)

    def post(self, request):
        payload = {
            'detail': 'Mock-проект создан.',
            'received_payload': request.data,
        }
        return Response(payload, status=201)


class ReportListGenerateView(APIView):
    required_permissions = {
        'GET': ('reports', 'read'),
        'POST': ('reports', 'generate'),
    }

    def get(self, request):
        data = [
            {'id': 101, 'title': 'Quarterly sales', 'format': 'pdf'},
            {'id': 102, 'title': 'Employee activity', 'format': 'xlsx'},
        ]
        return Response(data)

    def post(self, request):
        payload = {
            'detail': 'Mock-отчет поставлен в очередь на генерацию.',
            'received_payload': request.data,
        }
        return Response(payload, status=202)


class InvoiceListView(APIView):
    required_permissions = {
        'GET': ('invoices', 'read'),
    }

    def get(self, request):
        data = [
            {'id': 'INV-001', 'amount': 12500, 'currency': 'RUB'},
            {'id': 'INV-002', 'amount': 18300, 'currency': 'RUB'},
        ]
        return Response(data)
