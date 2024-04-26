"""
All SQLAlchemy related model setup
"""
from __future__ import annotations
from typing import List, TypeAlias

import discord
from typing_extensions import Annotated
from datetime import datetime
from sqlalchemy import (
    String,
    ForeignKey,
    Date,
    SmallInteger,
    BigInteger,
    Identity,
    Enum,
    Table,
    Column,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    relationship,
    Mapped,
    mapped_column,
)

DOT: TypeAlias = (
    discord.Guild | discord.Role | discord.abc.GuildChannel | discord.Member
)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


# Enum for permission values
class PermissionEnum(Enum):
    NONE = 0
    ALLOW = 1
    DENY = 2


discord_id_pk = Annotated[int, mapped_column(BigInteger, primary_key=True)]
name_str = Annotated[str, mapped_column(String(50))]


class DiscordCommons(MappedAsDataclass, init=False):
    # Mostly all Discord objects contain an id and name
    discord_object: DOT

    id: Mapped[discord_id_pk]
    name: Mapped[name_str]

    def __init__(self, discord_object: DOT):
        self.id: int = discord_object.id
        self.name: str = discord_object.name


region_int_pk = Annotated[int, mapped_column(Identity(), primary_key=True)]
message_len = Annotated[int, mapped_column(SmallInteger)]
discord_date = Annotated[datetime, mapped_column(Date)]
guild_fk = Annotated[int, mapped_column(ForeignKey("guild.id"))]
role_fk = Annotated[int, mapped_column(ForeignKey("role.id"))]
category_fk = Annotated[int, mapped_column(ForeignKey("category.id"))]


class Guild(DiscordCommons, Base):
    __tablename__ = "guild"

    # Bidirectional One-To-Many Relationships
    roles: Mapped[List[Role]] = relationship(
        back_populates="guild", default_factory=list
    )
    categories: Mapped[List[Category]] = relationship(
        back_populates="guild", default_factory=list
    )
    channels: Mapped[List[Channel]] = relationship(
        back_populates="guild", default_factory=list
    )
    members: Mapped[List[Member]] = relationship(
        secondary="member_guild", back_populates="guilds", default_factory=list
    )


class Role(DiscordCommons, Base):
    __tablename__ = "role"

    # Attributes
    color: Mapped[int]
    bot_managed: Mapped[bool]
    position: Mapped[int]
    guild_id: Mapped[guild_fk]
    perms_value: Mapped[int] = mapped_column(BigInteger)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id"), default=None)

    # Relationships
    guild: Mapped[Guild] = relationship(back_populates="roles", default=None)
    region: Mapped[Region] = relationship(back_populates="role", default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
    members: Mapped[List[Member]] = relationship(
        secondary="member_role", back_populates="roles", default_factory=list
    )

    def __init__(self, discord_object: discord.Role):
        super().__init__(discord_object)
        self.color: int = discord_object.color.value
        self.bot_managed: bool = discord_object.is_bot_managed()
        self.position: int = discord_object.position
        self.guild_id: int = discord_object.guild.id
        self.perms_value: int = discord_object.permissions.value
        self.guild: Guild = Guild(discord_object=discord_object.guild)

    def __repr__(self) -> str:
        return f"{self.name}"


class Region(Base):
    __tablename__ = "region"

    # Attributes
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]

    # Relationships
    role: Mapped[Role] = relationship(back_populates="region", default=None)

    def __repr__(self) -> str:
        return f"{self.name}"


class Category(DiscordCommons, Base):
    __tablename__ = "category"

    # Attributes
    guild_id: Mapped[guild_fk]
    permissions_synced: Mapped[bool]

    # Relationships
    guild: Mapped[Guild] = relationship(back_populates="categories", default=None)
    channels: Mapped[List[Channel]] = relationship(
        back_populates="category", default_factory=list
    )

    def __init__(self, discord_object: discord.CategoryChannel):
        super().__init__(discord_object)
        self.guild_id: int = discord_object.guild.id
        self.permissions_synced: bool = discord_object.permissions_synced
        self.guild: Guild = Guild(discord_object=discord_object.guild)


class Channel(DiscordCommons, Base):
    __tablename__ = "channel"

    # Attributes
    guild_id: Mapped[guild_fk]
    category_id: Mapped[category_fk | None] = mapped_column(default=None)

    # Relationships
    guild: Mapped[Guild] = relationship(back_populates="channels", default=None)
    category: Mapped[Category] = relationship(back_populates="channels", default=None)
    messages: Mapped[List[Message]] = relationship(
        back_populates="channel", default_factory=list
    )

    def __init__(
        self,
        discord_object: discord.abc.GuildChannel,
    ):
        super().__init__(discord_object)
        self.guild_id: int = discord_object.guild.id
        self.category_id: int = (
            discord_object.category.id if discord_object.category else None
        )
        self.guild: Guild = Guild(discord_object=discord_object.guild)
        self.category: Category | None = (
            Category(discord_object=discord_object.category)
            if discord_object.category
            else None
        )


class Member(DiscordCommons, Base):
    __tablename__ = "member"

    nick: Mapped[str | None]
    display_name: Mapped[str]

    roles: Mapped[List[Role]] = relationship(
        secondary="member_role", back_populates="members", default_factory=list
    )
    messages: Mapped[List[Message]] = relationship(
        back_populates="member", default_factory=list
    )
    guilds: Mapped[List[Guild]] = relationship(
        secondary="member_guild", back_populates="members", default_factory=list
    )

    def __init__(self, discord_object: discord.Member):
        super().__init__(discord_object)
        self.nick: str = discord_object.nick
        self.display_name: str = discord_object.display_name
        self.roles: List[Role] = [
            Role(discord_object=role) for role in discord_object.roles
        ]


class Message(DiscordCommons, Base):
    __tablename__ = "message"

    message_len: Mapped[int]
    created_at: Mapped[datetime]

    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channel.id"))

    member: Mapped[Member] = relationship(
        back_populates="messages", default_factory=list
    )
    channel: Mapped[Channel] = relationship(
        back_populates="messages", default_factory=list
    )

    deleted: Mapped[bool] = mapped_column(default=False)
    edited: Mapped[bool] = mapped_column(default=False)


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    value: Mapped[int]


member_guild = Table(
    "member_guild",
    Base.metadata,
    Column("member_id", ForeignKey("member.id"), primary_key=True),
    Column("guild_id", ForeignKey("guild.id"), primary_key=True),
)

member_role = Table(
    "member_role",
    Base.metadata,
    Column("member_id", ForeignKey("member.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)
