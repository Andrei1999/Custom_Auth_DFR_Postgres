from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import BasePermission

from .services import user_has_permission


class RequiredAccessPermission(BasePermission):
    message = 'Недостаточно прав для выполнения операции.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)

        if getattr(view, 'require_authenticated_user', False) and not user:
            raise NotAuthenticated('Пользователь не аутентифицирован.')

        required = getattr(view, 'required_permissions', None)
        if not required:
            return True

        if isinstance(required, dict):
            required = required.get(request.method)

        if required is None:
            return True

        if not user:
            raise NotAuthenticated('Пользователь не аутентифицирован.')

        resource, action = required
        if not user_has_permission(user, resource, action):
            raise PermissionDenied(self.message)
        return True
