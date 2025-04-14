from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from app.core.security import (
    ACCESS_TOKEN,
    PAYLOAD_KEY_SUB,
    PAYLOAD_KEY_TOKEN_TYPE,
    decode_jwt,
)
from app.database import crud
from app.database.db import db_helper
from app.database.redis_db import redis_helper
from app.models.user import User

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token/")


SessionDep = Annotated["AsyncSession", Depends(db_helper.get_session)]
RedisDep = Annotated["Redis", Depends(redis_helper.get_client)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_token_payload(token: TokenDep, redis: RedisDep):
    try:
        payload = decode_jwt(token=token)
        jti = payload["jti"]
        if await redis.get("blacklist:%s" % jti):
            raise InvalidTokenError

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    return payload


async def get_current_user(
    session: SessionDep,
    payload: Annotated[dict, Depends(get_current_token_payload)],
) -> User:
    if payload.get(PAYLOAD_KEY_TOKEN_TYPE) != ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    email = payload[PAYLOAD_KEY_SUB]
    user = await crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
