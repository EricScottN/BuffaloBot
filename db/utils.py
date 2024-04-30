from typing import List
from datetime import datetime, timedelta
import discord

from buffalobot import BuffaloBot
import db


async def refresh_db(bot: BuffaloBot):
    for guild in bot.guilds:
        guild_model = db.Guild(discord_object=guild)
        for role in guild.roles:
            guild_model.roles.append(db.Role(discord_object=role))
        for channel in guild.channels:
            guild_model.channels.append(db.Channel(discord_object=channel))
        for category in guild.categories:
            guild_model.categories.append(db.Category(discord_object=category))
        for member in guild.members:
            guild_model.members.append(db.Member(discord_object=member))
        async with bot.session() as session:
            assert guild_model not in session
            await session.merge(guild_model)
            await session.commit()


async def refresh_messages(bot: BuffaloBot):
    for guild in bot.guilds:
        for channel in guild.text_channels:
            async with bot.session() as session:
                async for message in channel.history(after=datetime.now() - timedelta(days=90)):
                    message_model = db.Message(discord_object=message)
                    await session.merge(message_model)
    await session.commit()
