from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.database import crud
from app.database.db import db_helper
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/auth", tags=["auth"])


SessionDep = Annotated["AsyncSession", Depends(db_helper.get_session)]


@router.post("/register", response_model=UserPublic)
async def create_user(session: SessionDep, user_in: UserCreate) -> User:
    user = await crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = await crud.create_user(session=session, user_create=user_in)
    return user
