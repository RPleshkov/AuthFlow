import asyncio
import logging

from app.database.db import db_helper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Creating initial data")
    await db_helper.init_db()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
