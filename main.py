""" Main script"""
import os
import logging
import asyncio

from aiohttp import ClientSession

from buffalobot.buffalobot import BuffaloBot, setup_db_engine
from helpers.discord_logger import setup_logging


logger = logging.getLogger(__name__)


async def main():
    await setup_logging()
    extensions = [
        f"startup_cogs.{filename[:-3]}" for filename in os.listdir("startup_cogs") if filename.endswith(".py")
    ]
    async with ClientSession() as client:
        session = await setup_db_engine()
        async with BuffaloBot(
                web_client=client,
                initial_extensions=extensions,
                session=session,
                testing_guild_id=1021399801222397983
        ) as bot:
            await bot.start(os.environ["DISCORD_TOKEN_KEY"])

asyncio.run(main())
