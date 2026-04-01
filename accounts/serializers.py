from rest_framework import serializers

from .models import Permission, Role, User
from .services import normalize_email


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'last_name',
            'first_name',
            'middle_name',
            'email',
            'is_active',
            'roles',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_active', 'roles', 'created_at', 'updated_at']

    def get_roles(self, obj):
        return [user_role.role.name for user_role in obj.user_roles.select_related('role').all()]


class RegisterSerializer(serializers.Serializer):
    last_name = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)
    middle_name = serializers.CharField(max_length=100, allow_blank=True, required=False, default='')
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    password_repeat = serializers.CharField(write_only=True, min_length=8, max_length=128)

    def validate_email(self, value):
        email = normalize_email(value)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return email

    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError({'password_repeat': 'Пароли не совпадают.'})
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, max_length=128)


class ProfileUpdateSerializer(serializers.Serializer):
    last_name = serializers.CharField(max_length=100, required=False)
    first_name = serializers.CharField(max_length=100, required=False)
    middle_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(max_length=254, required=False)

    def validate_email(self, value):
        email = normalize_email(value)
        user = self.context['request'].user
        exists = User.objects.filter(email=email).exclude(id=user.id).exists()
        if exists:
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return email


class PermissionSerializer(serializers.ModelSerializer):
    code = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ['id', 'resource', 'action', 'code', 'description', 'created_at']
        read_only_fields = ['id', 'code', 'created_at']

    def get_code(self, obj):
        return f'{obj.resource}:{obj.action}'

    def validate(self, attrs):
        resource = attrs.get('resource')
        action = attrs.get('action')
        queryset = Permission.objects.filter(resource=resource, action=action)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Такое разрешение уже существует.')
        return attrs


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'created_at']
        read_only_fields = ['id', 'permissions', 'created_at']

    def get_permissions(self, obj):
        permissions = obj.role_permissions.select_related('permission').all()
        return [
            {
                'id': item.permission.id,
                'resource': item.permission.resource,
                'action': item.permission.action,
                'code': f'{item.permission.resource}:{item.permission.action}',
            }
            for item in permissions
        ]


class RolePermissionAttachSerializer(serializers.Serializer):
    permission_id = serializers.IntegerField(min_value=1)


class UserRoleAttachSerializer(serializers.Serializer):
    role_id = serializers.IntegerField(min_value=1)
