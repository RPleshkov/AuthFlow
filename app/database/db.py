from typing import AsyncGenerator

from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


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


db_helper = DatabaseHelper(
    url=str(settings.postgres.get_uri),
    pool_size=settings.postgres.pool_size,
    max_overflow=settings.postgres.max_overflow,
    echo=settings.postgres.echo,
)
