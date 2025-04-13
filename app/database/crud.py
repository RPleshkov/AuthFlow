from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    user = User(
        email=email,
        password=hash_password(password),
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
