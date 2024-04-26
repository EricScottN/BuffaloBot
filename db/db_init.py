"""
Module to initialize database
"""

import logging
import discord
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from discord.ext import tasks, commands
from db.models import Guild, Member, Role, Category, Channel
from buffalobot import BuffaloBot

logger = logging.getLogger(__name__)


async def upsert_guild(bot: BuffaloBot, guild: discord.Guild):
    """
    Unused method but provides good query methods
    """
    async with bot.session() as session:
        guild_model = await session.get(
            Guild, guild.id, options=[selectinload(Guild.members)]
        )
        guild_model = (
            await session.scalars(
                select(Guild).filter_by(id=guild.id).options(selectinload(Guild.roles))
            )
        ).one()
        return guild_model


class Database(commands.Cog):
    """
    Discord.py cog class
    """

    def __init__(self, bot: BuffaloBot) -> None:
        self.bot = bot
        self.init_db.start()

    async def cog_unload(self) -> None:
        """
        Discord.py method for unloading Cog
        """
        self.init_db.stop()

    @tasks.loop(seconds=60)
    async def init_db(self):
        """
        Discord.py task to refresh database on init and every 24 hours
        """
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            guild_model = Guild(discord_object=guild)
            for role in guild.roles:
                guild_model.roles.append(Role(discord_object=role))
            for channel in guild.channels:
                guild_model.channels.append(Channel(discord_object=channel))
            for category in guild.categories:
                guild_model.categories.append(Category(discord_object=category))
            for member in guild.members:
                guild_model.members.append(Member(discord_object=member))
            async with self.bot.session() as session:
                await session.merge(guild_model)
                await session.commit()


async def setup(bot: BuffaloBot) -> None:
    """
    Discord.py setup function to initialize Cog
    """
    await bot.add_cog(Database(bot))
