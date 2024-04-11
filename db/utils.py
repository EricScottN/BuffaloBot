from typing import Sequence

import discord
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Guild


async def insert_guilds(
        session: AsyncSession,
        guilds: Sequence[discord.Guild]
):

    async with session.begin():
        session.add_all(
            [
                Guild(
                    id=guild.id,
                    name=guild.name
                ) for guild in guilds
            ]
        )
        await session.commit()
