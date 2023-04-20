"""
Database event updater.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio
from carbonbot.bot import CarbonBot
from carbonbot.config import logger
from carbonbot.db import EventUpdater

bot = CarbonBot(
    mode="single",
    polling_interval=1,
    update_pools=False,
    # drop_tables=False
)

updater = EventUpdater(
    db=bot.db,
    poll_interval=bot.polling_interval,
    test_mode=False
)


async def create_tasks_and_run(updater):
    tasks = []
    logger.info("Creating tasks")
    for args in updater.filters:
        exchange, _filter = args['exchange'], args['_filter']
        task = asyncio.create_task(updater._log_loop(exchange, _filter))
        tasks.append(task)
        logger.info(exchange, _filter)

    await asyncio.gather(*tasks)

try:
    asyncio.run(create_tasks_and_run(updater))
except KeyboardInterrupt:
    print("Stopped by user")
