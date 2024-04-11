""" Main script"""

import logging
import asyncio

from aiohttp import ClientSession

from buffalobot.buffalobot import start_bot, setup_db_engine
from helpers.discord_logger import setup_logging

logger = logging.getLogger(__name__)


async def main():
    await setup_logging()
    extensions = ["startup_cogs.listeners", "startup_cogs.mod_commands"]
    async with ClientSession() as client:
        engine = await setup_db_engine()
        await start_bot(extensions, client, engine=engine)


asyncio.run(main())
