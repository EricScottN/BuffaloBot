import logging
from discord.ext import tasks, commands
from db.models import Guild, Role, Region
from db.utils import insert_guilds, insert_roles
from buffalobot import BuffaloBot
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import load_only

logger = logging.getLogger(__name__)


class Database(commands.Cog):
    def __init__(self, bot: BuffaloBot) -> None:
        self.bot = bot
        self.init_db.start()

    def cog_unload(self) -> None:
        self.init_db.stop()

    @tasks.loop(seconds=60)
    async def init_db(self):
        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            guild_model = Guild(
                id=guild.id,
                name=guild.name
            )
            for role in guild.roles:
                async with self.bot.session() as session:
                    stmt = select(Region).where(Region.name == role.name).options(load_only(Region.name))
                    result = await session.execute(stmt)
                    region = result.scalars().first()
                guild_model.roles.append(
                    Role(
                        id=role.id,
                        name=role.name,
                        guild_id=guild.id,
                        region_id=region.id if region else None,
                        region=region if region else None
                    )
                )
            async with self.bot.session.begin() as session:
                await session.merge(guild_model)
                await session.commit()

async def setup(bot: BuffaloBot) -> None:
    await bot.add_cog(Database(bot))
