""" Main script"""

import logging
import asyncio
import os
from typing import List, Optional

import discord
from aiohttp import ClientSession
from discord.ext import commands
from asyncpg import create_pool, Pool

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
        db_pool: Pool,
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
        self.db_pool = db_pool
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
        print(self.db_pool)
        print(self.user, "is ready.")


async def setup_db_pool():
    try:
        return await create_pool(
            host=os.environ["POSTGRES_HOST"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )
    except Exception as e:
        logger.warning(e)
        return None


async def main():
    await setup_logging()
    extensions = ["startup_cogs.listeners", "startup_cogs.mod_commands"]
    async with ClientSession() as client:
        pool = await setup_db_pool()
        if pool:
            async with pool:
                await start_bot(extensions, client, pool=pool)
        else:
            await start_bot(extensions, client, pool=None)


async def start_bot(exts, our_client, pool):
    async with BuffaloBot(
        db_pool=pool,
        web_client=our_client,
        initial_extensions=exts,
        testing_guild_id=1021399801222397983,
    ) as bot:
        await bot.start(os.environ["DISCORD_TOKEN_KEY"])


asyncio.run(main())
