from typing import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings


class RedisHelper:
    def __init__(
        self,
        url: str,
        max_connections: int,
        decode_responses: bool,
    ) -> None:
        self.pool = ConnectionPool.from_url(
            url=url,
            max_connections=max_connections,
            decode_responses=decode_responses,
        )

    async def get_client(self) -> AsyncGenerator[Redis, None]:
        async with Redis.from_pool(self.pool) as client:
            yield client


redis_helper = RedisHelper(
    url=str(settings.redis.get_uri),
    max_connections=settings.redis.max_connections,
    decode_responses=settings.redis.decode_responses,
)
