from typing import List
from datetime import datetime, timedelta
import discord

from buffalobot import BuffaloBot
import db


async def refresh_db(bot: BuffaloBot):
    async with bot.session() as session:
        for guild in bot.guilds:
            guild_model = db.Guild(discord_object=guild)
            await session.merge(guild_model)
            for role in guild.roles:
                role_model = db.Role(discord_object=role)
                for member in role.members:
                    role_model.members.append(db.Member(discord_object=member))
                await session.merge(role_model)
                guild_model.roles.append(db.Role(discord_object=role))
            for channel in guild.channels:
                guild_model.channels.append(db.Channel(discord_object=channel))
            for category in guild.categories:
                guild_model.categories.append(db.Category(discord_object=category))
            for member in guild.members:
                guild_model.members.append(db.Member(discord_object=member))

            await session.merge(guild_model)
            await session.commit()


async def refresh_messages(bot: BuffaloBot):
    for guild in bot.guilds:
        for channel in guild.text_channels:
            channel_model = db.Channel(discord_object=channel)
            async with bot.session() as session:
                async for message in channel.history(after=datetime.now() - timedelta(days=90)):
                    member_model = db.Member(discord_object=message.author)
                    message_model = db.Message(discord_object=message)
                    message_model.member = member_model
                    channel_model.messages.append(message_model)
            await session.merge(channel_model)
            await session.commit()
