import logging
from discord.ext import tasks, commands
from discord import Guild
from db.models import Guild
from db.utils import insert_guilds
from buffalobot import BuffaloBot
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


class Database(commands.Cog):
    def __init__(self, bot: BuffaloBot) -> None:
        self.bot = bot
        self.engine = self.bot.engine
        self.init_db.start()

    def cog_unload(self) -> None:
        self.init_db.stop()

    @tasks.loop(seconds=60)
    async def init_db(self):
        await self.bot.wait_until_ready()
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        async with async_session() as session:
            await insert_guilds(session, self.bot.guilds)


async def setup(bot: BuffaloBot) -> None:
    await bot.add_cog(Database(bot))
