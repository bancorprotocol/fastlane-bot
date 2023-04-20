"""
Database event updater.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import asyncio

from carbon.bot import CarbonBot
from carbon.models import *
from carbon.updater import EventUpdater

bot = CarbonBot(
    mode="single",
    polling_interval=1,
    update_pools=True,
)

updater = EventUpdater(
    db=bot.db,
    poll_interval=bot.polling_interval,
)


async def create_tasks_and_run(updater: EventUpdater):
    """
    Run the event updater asynchronously with asyncio.

    Parameters
    ----------
    updater : EventUpdater
        The event updater object to run.
    """
    tasks = []
    for args in updater.filters:
        task = asyncio.create_task(updater._log_loop(args['exchange'], args['_filter']))
        tasks.append(task)
        logger.info(f"EventUpdater executing task for {args['exchange']} {args['_filter']}")
    await asyncio.gather(*tasks)

async def create_tasks_and_run(updater):
    tasks = []

    for args in updater.filters:
        exchange, _filter = args['exchange'], args['_filter']
        task = asyncio.create_task(updater._log_loop(exchange, _filter))
        tasks.append(task)
        print(exchange, _filter)

    await asyncio.gather(*tasks)

try:
    asyncio.run(create_tasks_and_run(updater))
except KeyboardInterrupt:
    print("Stopped by user")