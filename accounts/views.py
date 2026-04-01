from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Permission, Role, RolePermission, User, UserRole
from .serializers import (
    LoginSerializer,
    PermissionSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    RolePermissionAttachSerializer,
    RoleSerializer,
    UserRoleAttachSerializer,
    UserSerializer,
)
from .services import AuthError, authenticate_user, create_user, get_effective_permissions, issue_session, soft_delete_user


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = create_user(
            last_name=data['last_name'],
            first_name=data['first_name'],
            middle_name=data.get('middle_name', ''),
            email=data['email'],
            password=data['password'],
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = authenticate_user(data['email'], data['password'])
        except AuthError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        raw_token, session = issue_session(
            user=user,
            user_agent=request.headers.get('User-Agent', ''),
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        return Response(
            {
                'token_type': 'Session',
                'access_token': raw_token,
                'expires_at': session.expires_at,
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    require_authenticated_user = True
    required_permissions = None

    def post(self, request):
        session = request.auth
        if not session:
            return Response({'detail': 'Пользователь не аутентифицирован.'}, status=status.HTTP_401_UNAUTHORIZED)
        session.revoked_at = session.revoked_at or timezone.now()
        session.save(update_fields=['revoked_at'])
        return Response({'detail': 'Выход выполнен успешно.'}, status=status.HTTP_200_OK)


class MeView(APIView):
    require_authenticated_user = True
    required_permissions = None

    def get(self, request):
        return Response(
            {
                'user': UserSerializer(request.user).data,
                'effective_permissions': [
                    f'{permission.resource}:{permission.action}'
                    for permission in get_effective_permissions(request.user)
                ],
            }
        )

    def patch(self, request):
        serializer = ProfileUpdateSerializer(data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(request.user, field, value)
        request.user.save()
        return Response(UserSerializer(request.user).data)

    def delete(self, request):
        soft_delete_user(request.user)
        return Response({'detail': 'Аккаунт деактивирован и все сессии отозваны.'}, status=status.HTTP_200_OK)


class PermissionListCreateView(APIView):
    required_permissions = {
        'GET': ('access_rules', 'read'),
        'POST': ('access_rules', 'manage'),
    }

    def get(self, request):
        permissions = Permission.objects.all()
        return Response(PermissionSerializer(permissions, many=True).data)

    def post(self, request):
        serializer = PermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission = serializer.save()
        return Response(PermissionSerializer(permission).data, status=status.HTTP_201_CREATED)


class RoleListCreateView(APIView):
    required_permissions = {
        'GET': ('access_rules', 'read'),
        'POST': ('access_rules', 'manage'),
    }

    def get(self, request):
        roles = Role.objects.all().prefetch_related('role_permissions__permission')
        return Response(RoleSerializer(roles, many=True).data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)


class RolePermissionManageView(APIView):
    required_permissions = {'POST': ('access_rules', 'manage'), 'DELETE': ('access_rules', 'manage')}

    @transaction.atomic
    def post(self, request, role_id: int):
        serializer = RolePermissionAttachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = get_object_or_404(Role, pk=role_id)
        permission = get_object_or_404(Permission, pk=serializer.validated_data['permission_id'])
        RolePermission.objects.get_or_create(role=role, permission=permission)
        return Response(RoleSerializer(role).data)

    @transaction.atomic
    def delete(self, request, role_id: int, permission_id: int):
        role = get_object_or_404(Role, pk=role_id)
        permission = get_object_or_404(Permission, pk=permission_id)
        RolePermission.objects.filter(role=role, permission=permission).delete()
        return Response(RoleSerializer(role).data)


class AdminUserListView(APIView):
    required_permissions = ('access_rules', 'read')

    def get(self, request):
        users = User.objects.all().prefetch_related('user_roles__role')
        return Response(UserSerializer(users, many=True).data)


class UserRoleManageView(APIView):
    required_permissions = {'POST': ('access_rules', 'manage'), 'DELETE': ('access_rules', 'manage')}

    @transaction.atomic
    def post(self, request, user_id: int):
        serializer = UserRoleAttachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, pk=user_id)
        role = get_object_or_404(Role, pk=serializer.validated_data['role_id'])
        UserRole.objects.get_or_create(user=user, role=role)
        return Response(UserSerializer(user).data)

    @transaction.atomic
    def delete(self, request, user_id: int, role_id: int):
        user = get_object_or_404(User, pk=user_id)
        role = get_object_or_404(Role, pk=role_id)
        UserRole.objects.filter(user=user, role=role).delete()
        return Response(UserSerializer(user).data)
