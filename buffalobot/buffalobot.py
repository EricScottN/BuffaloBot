"""
Module that handles set up of bot
"""

import os
import logging
from typing import List

import discord
from aiohttp import ClientSession
from discord.ext import commands
from sqlalchemy import URL

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from db.models import Base

from helpers.role_select import RoleView

logger = logging.getLogger(__name__)


class BuffaloBot(commands.Bot):
    """
    Main Bot Class
    """

    def __init__(
        self,
        *args,
        web_client: ClientSession,
        initial_extensions: List[str],
        session: async_sessionmaker,
        testing_guild_id: int | None,
        **kwargs,
    ):
        intents: discord.Intents = discord.Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned, intents=intents, *args, **kwargs
        )
        self.initial_extensions = initial_extensions
        self.session = session
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

    async def on_ready(self):
        """
        Discord.py function for on_ready
        """
        print(self.session)
        print(self.user, "is ready.")


async def setup_db_engine() -> async_sessionmaker | None:
    """
    Sets up sqlalchemy engine / sessionmaker
    """
    try:
        engine = create_async_engine(
            URL.create(
                "postgresql+asyncpg",
                username=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
                host=os.environ["POSTGRES_HOST"],
                database="buffalobot",
            ),
            echo=True,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return async_sessionmaker(engine, expire_on_commit=False)
    except ConnectionRefusedError as e:
        logger.warning(e)
        return None
