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
class MyBot(commands.Bot):
    def __init__(self, *args,
                 initial_extensions: List[str],
                 db_pool: asyncpg.Pool,
                 web_client: ClientSession,
                 testing_guild_id: Optional[int] = None,
                 **kwargs):
        intents = discord.Intents.all()
        command_prefix = commands.when_mentioned
        super().__init__(command_prefix=command_prefix, intents=intents, *args, **kwargs)
        self.db_pool = db_pool
        self.bot_vars = env
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

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
        print(self.user, "is ready.")


async def main():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

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

    async with ClientSession() as our_client, asyncpg.create_pool(host="db", user="postgres", password="password") as pool:
        exts = ['startup_cogs.listeners', 'startup_cogs.mod_commands', 'startup_cogs.buf_commands']
        async with MyBot(db_pool=pool,
                         web_client=our_client,
                         initial_extensions=exts) as bot:
            await bot.start(env['TOKEN'])

asyncio.run(main())


# if __name__ == '__main__':
#     bot = MyBot()
#     try:
#         bot.run(bot.bot_vars['TOKEN'], log_handler=handler, log_level=logging.DEBUG)
#     except Exception as e:
#         print(e)
