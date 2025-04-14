from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.database import crud
from app.models.user import User
from app.schemas import AdminCreate


class DatabaseHelper:
    def __init__(
        self,
        url: str,
        pool_size: int,
        max_overflow: int,
        echo: bool = False,
    ) -> None:

        self.engine = create_async_engine(
            url=url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def init_db(self):
        async for session in self.get_session():
            user = (
                await session.execute(
                    select(User).where(User.email == settings.first_admin)
                )
            ).first()
            if not user:
                user_in = AdminCreate(
                    email=settings.first_admin,
                    password=settings.first_admin_password,
                )
                user = crud.create_user(session=session, user_create=user_in)


db_helper = DatabaseHelper(
    url=str(settings.postgres.get_uri),
    pool_size=settings.postgres.pool_size,
    max_overflow=settings.postgres.max_overflow,
    echo=settings.postgres.echo,
)
