from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, validate_password
from app.models import User
from app.schemas import UserCreate


async def create_user(session: AsyncSession, user_create: UserCreate) -> User:
    params = user_create.model_dump()
    params["password"] = hash_password(params["password"])
    user = User(**params)

    session.add(user)
    await session.commit()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = await session.execute(stmt)
    return user.scalar_one_or_none()


async def authenticate(session: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(session=session, email=email)
    if not user:
        return None
    if not validate_password(password, user.password):
        return None
    return user


async def verify_user(session: AsyncSession, email: str) -> None:
    stmt = (
        update(User)
        .where(User.email == email)
        .values(
            is_verified=True,
        )
    )
    await session.execute(stmt)
    await session.commit()
