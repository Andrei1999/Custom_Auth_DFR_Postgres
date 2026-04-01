from django.core.management.base import BaseCommand

from accounts.models import Permission, Role, RolePermission, User, UserRole
from accounts.security import hash_password


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми ролями, правами и пользователями.'

    def handle(self, *args, **options):
        permission_map = [
            ('access_rules', 'read', 'Просмотр ролей и разрешений'),
            ('access_rules', 'manage', 'Изменение ролей и разрешений'),
            ('projects', 'read', 'Просмотр списка проектов'),
            ('projects', 'create', 'Создание проекта'),
            ('reports', 'read', 'Просмотр отчетов'),
            ('reports', 'generate', 'Генерация отчета'),
            ('invoices', 'read', 'Просмотр счетов'),
        ]
        permissions = {}
        for resource, action, description in permission_map:
            permissions[(resource, action)], _ = Permission.objects.get_or_create(
                resource=resource,
                action=action,
                defaults={'description': description},
            )

        role_permissions = {
            'admin': [
                ('access_rules', 'read'),
                ('access_rules', 'manage'),
                ('projects', 'read'),
                ('projects', 'create'),
                ('reports', 'read'),
                ('reports', 'generate'),
                ('invoices', 'read'),
            ],
            'viewer': [
                ('projects', 'read'),
                ('reports', 'read'),
            ],
            'editor': [
                ('projects', 'read'),
                ('projects', 'create'),
                ('reports', 'read'),
                ('reports', 'generate'),
            ],
            'accountant': [
                ('invoices', 'read'),
            ],
        }

        roles = {}
        for role_name, links in role_permissions.items():
            roles[role_name], _ = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': f'Системная роль {role_name}'},
            )
            for resource, action in links:
                RolePermission.objects.get_or_create(
                    role=roles[role_name],
                    permission=permissions[(resource, action)],
                )

        demo_users = [
            ('admin@example.com', 'Admin123', 'Иванов', 'Иван', 'Иванович', ['admin']),
            ('viewer@example.com', 'Viewer123', 'Петров', 'Петр', 'Петрович', ['viewer']),
            ('editor@example.com', 'Editor123', 'Сидоров', 'Сидор', 'Сидорович', ['editor']),
            ('inactive@example.com', 'Inactive123', 'Смирнова', 'Анна', 'Олеговна', ['viewer']),
        ]

        for email, password, last_name, first_name, middle_name, assigned_roles in demo_users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'last_name': last_name,
                    'first_name': first_name,
                    'middle_name': middle_name,
                    'password_hash': hash_password(password),
                    'is_active': email != 'inactive@example.com',
                },
            )
            if not created and not user.password_hash:
                user.password_hash = hash_password(password)
                user.save(update_fields=['password_hash'])
            for role_name in assigned_roles:
                UserRole.objects.get_or_create(user=user, role=roles[role_name])

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены.'))
