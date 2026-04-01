from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Permission, Role, RolePermission, SessionToken, User, UserRole
from .security import generate_session_token, hash_password, hash_session_token, verify_password

SESSION_LIFETIME_DAYS = 7


class AuthError(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


@transaction.atomic
def create_user(*, last_name: str, first_name: str, middle_name: str, email: str, password: str) -> User:
    email = normalize_email(email)
    if User.objects.filter(email=email).exists():
        raise AuthError('Пользователь с таким email уже существует.')

    user = User.objects.create(
        last_name=last_name.strip(),
        first_name=first_name.strip(),
        middle_name=middle_name.strip(),
        email=email,
        password_hash=hash_password(password),
        is_active=True,
    )
    viewer_role = Role.objects.filter(name='viewer').first()
    if viewer_role:
        UserRole.objects.get_or_create(user=user, role=viewer_role)
    return user


def authenticate_user(email: str, password: str) -> User:
    email = normalize_email(email)
    user = User.objects.filter(email=email).first()
    if not user:
        raise AuthError('Неверный email или пароль.')
    if not user.is_active:
        raise AuthError('Учетная запись деактивирована.')
    if not verify_password(password, user.password_hash):
        raise AuthError('Неверный email или пароль.')
    return user


@transaction.atomic
def issue_session(*, user: User, user_agent: str = '', ip_address: str | None = None) -> tuple[str, SessionToken]:
    raw_token = generate_session_token()
    session = SessionToken.objects.create(
        user=user,
        token_hash=hash_session_token(raw_token),
        expires_at=timezone.now() + timedelta(days=SESSION_LIFETIME_DAYS),
        user_agent=(user_agent or '')[:255],
        ip_address=ip_address,
    )
    return raw_token, session


def get_session_by_raw_token(raw_token: str) -> SessionToken | None:
    token_hash = hash_session_token(raw_token)
    session = SessionToken.objects.select_related('user').filter(token_hash=token_hash).first()
    if not session or not session.is_valid:
        return None
    return session


def touch_session(session: SessionToken) -> None:
    SessionToken.objects.filter(pk=session.pk).update(last_used_at=timezone.now())


def revoke_session(raw_token: str) -> bool:
    token_hash = hash_session_token(raw_token)
    updated = SessionToken.objects.filter(token_hash=token_hash, revoked_at__isnull=True).update(revoked_at=timezone.now())
    return bool(updated)


def revoke_session_instance(session: SessionToken) -> None:
    if session.revoked_at is None:
        session.revoked_at = timezone.now()
        session.save(update_fields=['revoked_at'])


def revoke_all_user_sessions(user: User) -> int:
    return SessionToken.objects.filter(user=user, revoked_at__isnull=True).update(revoked_at=timezone.now())


@transaction.atomic
def soft_delete_user(user: User) -> User:
    user.is_active = False
    user.save(update_fields=['is_active', 'updated_at'])
    revoke_all_user_sessions(user)
    return user


def get_effective_permissions(user: User):
    return Permission.objects.filter(
        permission_roles__role__role_users__user=user,
    ).distinct()


def user_has_permission(user: User, resource: str, action: str) -> bool:
    if not user or not user.is_active:
        return False
    return Permission.objects.filter(
        resource=resource,
        action=action,
        permission_roles__role__role_users__user=user,
    ).exists()
