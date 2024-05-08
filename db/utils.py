from datetime import datetime, timedelta

import discord
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from buffalobot import BuffaloBot
import db


async def update_guild(
    async_session: async_sessionmaker[AsyncSession], guild: discord.Guild
):
    guild_model = db.Guild(discord_object=guild)
    async with async_session() as session:
        async with session.begin():
            await session.merge(guild_model)
    return guild_model


async def update_role(
    async_session: async_sessionmaker[AsyncSession], role: discord.Role
):
    role_model = db.Role(discord_object=role)
    for member in role.members:
        role_model.members.append(db.Member(discord_object=member))
    async with async_session() as session:
        async with session.begin():
            await session.merge(role_model)
    return role_model


async def update_channel(
    async_session: async_sessionmaker[AsyncSession], channel: discord.abc.GuildChannel
):
    channel_model = db.Channel(discord_object=channel)
    channel_model = await update_channel_overwrites(channel, channel_model)
    async with async_session() as session:
        async with session.begin():
            await session.merge(channel_model)
    return channel_model


async def refresh_db(bot: BuffaloBot):
    for guild in bot.guilds:
        guild_model = await update_guild(bot.session, guild)
        for role in guild.roles:
            role_model = await update_role(bot.session, role)
            guild_model.roles.append(role_model)
        for category in guild.categories:
            category_model = await update_channel(bot.session, category)
            guild_model.channels.append(category_model)
        for channel in guild.channels:
            channel_model = await update_channel(bot.session, channel)
            guild_model.channels.append(channel_model)
        for member in guild.members:
            guild_model.members.append(db.Member(discord_object=member))
        await update_guild(bot.session, guild)


async def update_channel_overwrites(
    channel: discord.abc.GuildChannel, channel_model: db.Channel
) -> db.Channel:
    for role_or_member, overwrite in channel.overwrites.items():
        value = dict(iter(overwrite))
        if isinstance(role_or_member, discord.Role):
            channel_model.role_overwrites.append(
                db.RoleOverwrite(
                    discord_role=role_or_member, discord_channel=channel, value=value
                )
            )
        if isinstance(role_or_member, discord.Member):
            channel_model.member_overwrites.append(
                db.MemberOverwrite(
                    discord_member=role_or_member, discord_channel=channel, value=value
                )
            )
    return channel_model


async def refresh_messages(bot: BuffaloBot):
    for guild in bot.guilds:
        for channel in guild.text_channels:
            channel_model = db.Channel(discord_object=channel)
            async with bot.session() as session:
                async for message in channel.history(
                    after=datetime.now() - timedelta(days=90)
                ):
                    member_model = db.Member(discord_object=message.author)
                    message_model = db.Message(discord_object=message)
                    message_model.member = member_model
                    channel_model.messages.append(message_model)
            await session.merge(channel_model)
            await session.commit()
