from typing import Sequence

import discord
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Guild, Role


async def insert_roles(
        session: AsyncSession,
        guild: discord.Guild,
        roles: Sequence[discord.Role]
):
    roles_models = [
        Role(
            id=role.id,
            name=role.name,
            guild_id=role.guild.id
        ) for role in roles
    ]
    async with session.begin():
        for role_model in roles_models:
            await session.merge(role_model)
        await session.commit()


async def insert_guilds(
        session: AsyncSession,
        guilds: Sequence[discord.Guild]
):
    guilds_models = [
        Guild(
            id=guild.id,
            name=guild.name
        ) for guild in guilds
    ]
    async with session.begin():
        for guild_model in guilds_models:
            await session.merge(guild_model)
        await session.commit()
