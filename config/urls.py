from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok'})


urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('api/', include('accounts.urls')),
    path('api/mock/', include('mock_api.urls')),
]
