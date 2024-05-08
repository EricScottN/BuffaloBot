"""
Module to initialize database
"""

import logging
from discord.ext import tasks, commands
from db.utils import refresh_messages, refresh_db

from buffalobot import BuffaloBot

logger = logging.getLogger(__name__)


class Database(commands.Cog):
    """
    Discord.py cog class
    """

    def __init__(self, bot: BuffaloBot) -> None:
        self.bot = bot
        self.refresh_db.start()

    async def cog_unload(self) -> None:
        """
        Discord.py method for unloading Cog
        """
        self.refresh_db.stop()

    @tasks.loop(hours=24)
    async def refresh_db(self):
        """
        Discord.py task to refresh database on init and every 24 hours
        """
        await self.bot.wait_until_ready()
        await refresh_db(self.bot)
        await refresh_messages(self.bot)


async def setup(bot: BuffaloBot) -> None:
    """
    Discord.py setup function to initialize Cog
    """
    await bot.add_cog(Database(bot))
