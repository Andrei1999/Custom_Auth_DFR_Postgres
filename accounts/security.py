import base64
import hashlib
import hmac
import secrets
from typing import Tuple


PASSWORD_ALGORITHM = 'pbkdf2_sha256'
PASSWORD_ITERATIONS = 260000
SALT_BYTES = 16
SESSION_TOKEN_BYTES = 32


def hash_password(password: str) -> str:
    salt = secrets.token_hex(SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        PASSWORD_ITERATIONS,
    )
    encoded = base64.b64encode(derived_key).decode('ascii')
    return f'{PASSWORD_ALGORITHM}${PASSWORD_ITERATIONS}${salt}${encoded}'


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_str, salt, encoded = stored_hash.split('$', 3)
        if algorithm != PASSWORD_ALGORITHM:
            return False
        iterations = int(iterations_str)
    except (ValueError, TypeError):
        return False

    recalculated = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations,
    )
    expected = base64.b64decode(encoded.encode('ascii'))
    return hmac.compare_digest(recalculated, expected)


def generate_session_token() -> str:
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
