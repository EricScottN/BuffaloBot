import os
import logging.handlers
import asyncio
import logging.handlers
from typing import List, Optional

import discord
from aiohttp import ClientSession
from discord.ext import commands
import asyncpg
from env import env


# comment to see if this works
class BuffaloBot(commands.Bot):
    def __init__(self, *args,
                 initial_extensions: List[str],
                 db_pool: asyncpg.Pool = None,
                 web_client: ClientSession,
                 testing_guild_id: Optional[int] = None,
                 **kwargs):
        intents = discord.Intents.all()
        command_prefix = commands.when_mentioned
        super().__init__(command_prefix=command_prefix, intents=intents, *args, **kwargs)
        self.initial_extensions = initial_extensions
        self.db_pool = db_pool
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.bot_vars = env

    async def setup_hook(self):
        for extension in self.initial_extensions:
            print(f"Extension loaded: {extension}")
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        print(self.db_pool)
        print(self.user, "is ready.")


async def main():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    root.addHandler(handler)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    max_retries = int(os.getenv("MAX_RETRIES", 0))

    async with ClientSession() as our_client:
        exts = ['startup_cogs.listeners', 'startup_cogs.mod_commands', 'startup_cogs.buf_commands']
        await db_conn(exts, max_retries, our_client)
        await start_bot(exts, our_client, pool=None)


async def db_conn(exts, max_retries, our_client):
    sleep_time = 5
    for i in range(max_retries):
        try:
            async with asyncpg.create_pool(host="db", user="postgres", password="password") as pool:
                return await start_bot(exts, our_client, pool)
        except Exception as e:
            print(f"Couldn't connect to db: {e}\n\n Sleeping for {sleep_time} seconds")
            await asyncio.sleep(5)
            continue


async def start_bot(exts, our_client, pool):
    async with BuffaloBot(db_pool=pool,
                          web_client=our_client,
                          initial_extensions=exts,
                          testing_guild_id=1021399801222397983) as bot:
        await bot.start(env['TOKEN'])

asyncio.run(main())
