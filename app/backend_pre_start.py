import asyncio
import logging

from sqlalchemy import select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.database.db import db_helper
from app.database.redis_db import redis_helper

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    try:

        async for session in db_helper.get_session():
            await session.execute(select(1))

        async for client in redis_helper.get_client():
            await client.ping()

    except Exception as e:
        logger.error(e)
        raise e


async def main() -> None:
    logger.info("Initializing services")
    await init()
    logger.info("Services finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
