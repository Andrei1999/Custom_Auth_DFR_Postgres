from django.db import models
from django.utils import timezone


class User(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['id']

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.email


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
        ordering = ['id']

    def __str__(self):
        return self.name


class Permission(models.Model):
    resource = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'permissions'
        ordering = ['resource', 'action']
        constraints = [
            models.UniqueConstraint(fields=['resource', 'action'], name='uniq_resource_action'),
        ]

    def __str__(self):
        return f'{self.resource}:{self.action}'


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_roles'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'role'], name='uniq_user_role'),
        ]


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_permissions'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['role', 'permission'], name='uniq_role_permission'),
        ]


class SessionToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token_hash'], name='session_token_hash_idx'),
            models.Index(fields=['expires_at'], name='session_expires_idx'),
        ]

    @property
    def is_valid(self):
        return self.revoked_at is None and self.expires_at > timezone.now() and self.user.is_active
