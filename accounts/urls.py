from django.urls import path

from .views import (
    AdminUserListView,
    LoginView,
    LogoutView,
    MeView,
    PermissionListCreateView,
    RegisterView,
    RoleListCreateView,
    RolePermissionManageView,
    UserRoleManageView,
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('admin/permissions/', PermissionListCreateView.as_view(), name='permission-list-create'),
    path('admin/roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('admin/roles/<int:role_id>/permissions/', RolePermissionManageView.as_view(), name='role-permission-attach'),
    path('admin/roles/<int:role_id>/permissions/<int:permission_id>/', RolePermissionManageView.as_view(), name='role-permission-delete'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<int:user_id>/roles/', UserRoleManageView.as_view(), name='user-role-attach'),
    path('admin/users/<int:user_id>/roles/<int:role_id>/', UserRoleManageView.as_view(), name='user-role-delete'),
]
