from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User
from app.schemas.user import UserCreate


async def create_user(session: AsyncSession, user_create: UserCreate) -> User:
    user = User(
        email=user_create.email,
        password=hash_password(user_create.password),
    )
    session.add(user)
    await session.commit()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = await session.execute(stmt)
    return user.scalar_one_or_none()


async def confirm_user(session: AsyncSession, email: str) -> None:
    stmt = (
        update(User)
        .where(User.email == email)
        .values(
            is_verified=True,
        )
    )
    await session.execute(stmt)
    await session.commit()
