import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Literal

import bcrypt
import jwt

from app.core.config import settings
from app.models.user import User

"""Функции хэширования и валидации пароля"""


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(
        password=password.encode(),
        salt=salt,
    )


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


"""Функции для работы с JWT"""


class TokenTypes(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFY = "verify"
    RESETPASS = "ressetpass"


PAYLOAD_KEY_TOKEN_TYPE = "type"
PAYLOAD_KEY_USER_ID = "user_id"
PAYLOAD_KEY_SUB = "sub"


def encode_jwt(
    payload: dict,
    private_key: str = settings.security.private_key.read_text(),
    algorithm: str = settings.security.jwt.algorithm,
    expire_minutes: int = settings.security.jwt.access_token_expire_minutes,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    jti = str(uuid.uuid4())
    to_encode.update(exp=expire, iat=now, jti=jti)
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )
    return encoded_jwt


def decode_jwt(
    token: str,
    public_key: str = settings.security.public_key.read_text(),
    algorithm: str = settings.security.jwt.algorithm,
):

    decoded_jwt = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded_jwt


def create_token_by_type(
    token_type: Literal[
        TokenTypes.ACCESS,
        TokenTypes.REFRESH,
        TokenTypes.VERIFY,
        TokenTypes.RESETPASS,
    ],
):
    def create_token(user: User):
        payload = {
            PAYLOAD_KEY_TOKEN_TYPE: token_type,
            PAYLOAD_KEY_USER_ID: str(user.id),
            PAYLOAD_KEY_SUB: user.email,
        }
        expire_map = {
            TokenTypes.ACCESS: None,
            TokenTypes.REFRESH: timedelta(
                days=settings.security.jwt.refresh_token_expire_days
            ),
            TokenTypes.VERIFY: timedelta(
                days=settings.security.jwt.verify_token_expire_days
            ),
            TokenTypes.RESETPASS: timedelta(
                minutes=settings.security.jwt.resetpass_token_expire_minutes
            ),
        }

        expires_delta = expire_map.get(token_type)
        return encode_jwt(payload=payload, expires_delta=expires_delta)

    return create_token
