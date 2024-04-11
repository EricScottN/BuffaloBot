""" Main script"""

import logging
import asyncio
import os
from typing import List, Optional

import discord
from aiohttp import ClientSession
from discord.ext import commands
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from db.models import Base

from helpers.discord_logger import setup_logging
from helpers.role_select import RoleView

logger = logging.getLogger(__name__)


class BuffaloBot(commands.Bot):
    """
    Main Bot Class
    """

    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        engine: AsyncEngine,
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        intents = discord.Intents.all()
        command_prefix = commands.when_mentioned
        super().__init__(
            command_prefix=command_prefix, intents=intents, *args, **kwargs
        )
        self.initial_extensions = initial_extensions
        self.engine = engine
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id

    async def setup_hook(self):
        """
        Discord.py setup_hook is run before on_ready
        """
        # Load extensions
        for extension in self.initial_extensions:
            print(f"Extension loaded: {extension}")
            await self.load_extension(extension)

        # S
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)
            self.add_view(RoleView())
            print("RoleView added")

        if self.engine:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def on_ready(self):
        print(self.engine)
        print(self.user, "is ready.")


async def setup_db_engine():
    try:
        return create_async_engine(
            URL.create("postgresql+asyncpg",
                       username=os.environ["POSTGRES_USER"],
                       password=os.environ["POSTGRES_PASSWORD"],
                       host=os.environ["POSTGRES_HOST"],
                       database="buffalobot")
        )
    except Exception as e:
        logger.warning(e)
        return None


async def main():
    await setup_logging()
    extensions = ["startup_cogs.listeners", "startup_cogs.mod_commands"]
    async with ClientSession() as client:
        engine = await setup_db_engine()
        await start_bot(extensions, client, engine=engine)


async def start_bot(exts: List[str], web_client: ClientSession, engine: Optional[AsyncEngine]):
    async with BuffaloBot(
        engine=engine,
        web_client=web_client,
        initial_extensions=exts,
        testing_guild_id=1021399801222397983,
    ) as bot:
        await bot.start(os.environ["DISCORD_TOKEN_KEY"])


asyncio.run(main())
