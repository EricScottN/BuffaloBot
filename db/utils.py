from typing import List

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
