import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import RedisDep, SessionDep, AccessTokenPayload, RefreshTokenPayload
from app.core.config import settings
from app.core.security import (
    PAYLOAD_KEY_SUB,
    PAYLOAD_KEY_TOKEN_TYPE,
    TokenTypes,
    create_token_by_type,
)
from app.database import crud
from app.models.user import User
from app.schemas import Token, UserCreate, UserPublic

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def create_user(session: SessionDep, user_in: UserCreate) -> User:
    user = await crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this email already exists in the system.",
        )

    user = await crud.create_user(session=session, user_create=user_in)
    logger.info("User successfully registered: %s" % user.email)
    return user


@router.post("/login")
async def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    access_token = create_token_by_type(TokenTypes.ACCESS)(user)
    refresh_token = create_token_by_type(TokenTypes.REFRESH)(user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    access_token: AccessTokenPayload,
    refresh_token: RefreshTokenPayload,
    redis: RedisDep,
):

    access_jti = access_token["jti"]
    refresh_jti = refresh_token["jti"]

    await redis.set(
        name=("blacklist:%s" % access_jti),
        value="revoked",
        ex=settings.security.jwt.access_token_expire_minutes * 60,
    )
    await redis.set(
        name=("blacklist:%s" % refresh_jti),
        value="revoked",
        ex=settings.security.jwt.refresh_token_expire_days * 24 * 60 * 60,
    )
    return None


@router.post("/refresh")
async def refresh(
    refresh_token: RefreshTokenPayload,
    session: SessionDep,
    redis: RedisDep,
) -> Token:

    payload = refresh_token.copy()
    if payload.get(PAYLOAD_KEY_TOKEN_TYPE) != TokenTypes.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user = await crud.get_user_by_email(
        session=session,
        email=payload[PAYLOAD_KEY_SUB],
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
        )

    refresh_jti = refresh_token["jti"]
    await redis.set(
        name=("blacklist:%s" % refresh_jti),
        value="revoked",
        ex=settings.security.jwt.refresh_token_expire_days * 24 * 60 * 60,
    )
    access_token = create_token_by_type(TokenTypes.ACCESS)(user)
    refresh_token = create_token_by_type(TokenTypes.REFRESH)(user)  # type: ignore

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,  # type: ignore
    )
