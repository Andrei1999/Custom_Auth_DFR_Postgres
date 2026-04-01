from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .services import get_session_by_raw_token, touch_session


class SessionHeaderAuthentication(BaseAuthentication):
    keyword = 'Session'

    def authenticate(self, request):
        raw_token = None
        authorization = request.headers.get('Authorization', '')
        header_token = request.headers.get('X-Session-Token', '')

        if authorization:
            prefix = f'{self.keyword} '
            if not authorization.startswith(prefix):
                raise AuthenticationFailed('Используйте заголовок Authorization: Session <token>.')
            raw_token = authorization[len(prefix):].strip()
        elif header_token:
            raw_token = header_token.strip()
        else:
            return None

        if not raw_token:
            raise AuthenticationFailed('Токен сессии не передан.')

        session = get_session_by_raw_token(raw_token)
        if session is None:
            raise AuthenticationFailed('Сессия не найдена, истекла или была отозвана.')

        touch_session(session)
        return (session.user, session)

    def authenticate_header(self, request):
        return self.keyword
