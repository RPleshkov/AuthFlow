import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, create_refresh_token
from app.database import crud
from app.database.db import db_helper
from app.database.redis_db import redis_helper
from app.models.user import User
from app.schemas import Token, UserCreate, UserPublic

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/auth", tags=["auth"])


SessionDep = Annotated["AsyncSession", Depends(db_helper.get_session)]
RedisDep = Annotated["Redis", Depends(redis_helper.get_client)]


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def create_user(session: SessionDep, user_in: UserCreate) -> User:
    user = await crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
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
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )
