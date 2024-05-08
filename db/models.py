"""
All SQLAlchemy related model setup
"""

from __future__ import annotations
from typing import List, TypeAlias, Dict, Any

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
    Table,
    Column,
    func,
    select,
    Select,
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    relationship,
    Mapped,
    mapped_column,
)

DOT: TypeAlias = (
    discord.Guild
    | discord.Role
    | discord.abc.GuildChannel
    | discord.Member
    | discord.Message
    | discord.User
)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


discord_id_pk = Annotated[int, mapped_column(BigInteger, primary_key=True)]
name_str = Annotated[str, mapped_column(String(50))]


class DiscordCommons(MappedAsDataclass, init=False):
    # Mostly all Discord objects contain an id and name
    discord_object: DOT

    id: Mapped[discord_id_pk]
    name: Mapped[name_str]
    is_active: Mapped[bool] = mapped_column(default=True)
    etl_modified: Mapped[datetime] = mapped_column(server_default=func.now())

    def __init__(self, discord_object: DOT):
        self.id: int = discord_object.id
        self.name: str = discord_object.name


region_int_pk = Annotated[int, mapped_column(Identity(), primary_key=True)]
message_len = Annotated[int, mapped_column(SmallInteger)]
discord_date = Annotated[datetime, mapped_column(Date)]
guild_fk = Annotated[int, mapped_column(ForeignKey("guild.id"))]
role_fk = Annotated[int, mapped_column(ForeignKey("role.id"))]


class Guild(DiscordCommons, Base):
    __tablename__ = "guild"

    # Bidirectional One-To-Many Relationships
    roles: Mapped[List[Role]] = relationship(
        back_populates="guild", default_factory=list
    )
    channels: Mapped[List[Channel]] = relationship(
        back_populates="guild", default_factory=list
    )
    members: Mapped[List[Member]] = relationship(
        secondary="member_guild", back_populates="guilds", default_factory=list
    )


class Region(Base):
    __tablename__ = "region"

    # Attributes
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]

    # Relationships
    role: Mapped[Role] = relationship(back_populates="region", default=None)

    def __repr__(self) -> str:
        return f"{self.name}"


class Role(DiscordCommons, Base):
    __tablename__ = "role"

    # Attributes
    color: Mapped[int]
    bot_managed: Mapped[bool]
    position: Mapped[int]
    guild_id: Mapped[guild_fk]
    permissions_value: Mapped[int] = mapped_column(BigInteger)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("region.id"), default=None)

    # Relationships
    guild: Mapped[Guild] = relationship(back_populates="roles", default=None)
    region: Mapped[Region] = relationship(back_populates="role")
    members: Mapped[List[Member]] = relationship(
        secondary="member_role", back_populates="roles", default_factory=list
    )
    channel_overwrites: Mapped[List[RoleOverwrite]] = relationship(
        back_populates="role"
    )

    def __init__(self, discord_object: discord.Role):
        super().__init__(discord_object)
        self.color: int = discord_object.color.value
        self.bot_managed: bool = discord_object.is_bot_managed()
        self.position: int = discord_object.position
        self.guild_id: int = discord_object.guild.id
        self.permissions_value: int = discord_object.permissions.value
        self.region_id: Select[tuple[Any]] = select(Region.id).where(
            Region.name == discord_object.name
        )


class Channel(DiscordCommons, Base):
    __tablename__ = "channel"

    id: Mapped[discord_id_pk] = mapped_column()

    # Attributes
    guild_id: Mapped[guild_fk]
    type: Mapped[str]
    category_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("channel.id"), default=None
    )

    # Relationships
    guild: Mapped[Guild] = relationship(back_populates="channels", default=None)
    channels: Mapped[List[Channel]] = relationship(
        back_populates="category", default_factory=list
    )
    category: Mapped[Channel] = relationship(
        back_populates="channels", default=None, remote_side=[id]
    )
    messages: Mapped[List[Message]] = relationship(
        back_populates="channel", default_factory=list
    )
    role_overwrites: Mapped[List[RoleOverwrite]] = relationship(
        back_populates="channel", default_factory=list
    )
    member_overwrites: Mapped[List[MemberOverwrite]] = relationship(
        back_populates="channel", default_factory=list
    )

    def __init__(
        self,
        discord_object: discord.abc.GuildChannel,
    ):
        super().__init__(discord_object)
        self.guild_id: int = discord_object.guild.id
        self.type: str = discord_object.type.name
        self.category_id: int = (
            discord_object.category.id if discord_object.category else None
        )


class Member(DiscordCommons, Base):
    __tablename__ = "member"

    is_bot: Mapped[bool]
    created_at: Mapped[datetime]
    display_name: Mapped[str]
    global_name: Mapped[str | None]
    permissions_value: Mapped[int | None] = mapped_column(BigInteger)

    nick: Mapped[str | None]
    roles: Mapped[List[Role]] = relationship(
        secondary="member_role", back_populates="members", default_factory=list
    )
    messages: Mapped[List[Message]] = relationship(
        back_populates="member", default_factory=list
    )
    guilds: Mapped[List[Guild]] = relationship(
        secondary="member_guild", back_populates="members", default_factory=list
    )
    channel_overwrites: Mapped[List[MemberOverwrite]] = relationship(
        back_populates="member"
    )

    def __init__(self, discord_object: discord.Member | discord.User):
        super().__init__(discord_object)
        self.is_bot: bool = discord_object.bot
        self.created_at: datetime = discord_object.created_at.replace(tzinfo=None)
        self.display_name: str = discord_object.display_name
        self.global_name: str = discord_object.global_name
        if isinstance(discord_object, discord.Member):
            self.nick: str = discord_object.nick
            self.display_name: str = discord_object.display_name
            self.permissions_value: str = discord_object.guild_permissions.value


class Message(Base):
    __tablename__ = "message"

    id: Mapped[discord_id_pk]

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

    def __init__(self, discord_object: discord.Message):
        super().__init__()
        self.id: int = discord_object.id
        self.message_len: int = len(discord_object.content)
        self.created_at: datetime = discord_object.created_at.replace(tzinfo=None)
        self.member_id: int = discord_object.author.id
        self.channel_id: int = discord_object.channel.id


class MemberOverwrite(Base):
    __tablename__ = "member_overwrite"

    channel_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("channel.id"), primary_key=True
    )
    member_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("member.id"), primary_key=True
    )
    value: Mapped[Dict] = mapped_column(JSONB)
    member: Mapped[Member] = relationship(back_populates="channel_overwrites")
    channel: Mapped[Channel] = relationship(back_populates="member_overwrites")

    def __init__(
        self,
        discord_member: discord.Member,
        discord_channel: discord.abc.GuildChannel,
        value: Dict,
    ):
        super().__init__()
        self.channel_id: int = discord_channel.id
        self.value: Dict = value
        self.member_id: int = discord_member.id


class RoleOverwrite(Base):
    __tablename__ = "role_overwrite"
    channel_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("channel.id"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("role.id"), primary_key=True
    )
    value: Mapped[Dict] = mapped_column(JSONB)
    role: Mapped[Role] = relationship(back_populates="channel_overwrites")
    channel: Mapped[Channel] = relationship(back_populates="role_overwrites")

    def __init__(
        self,
        discord_role: discord.Role,
        discord_channel: discord.abc.GuildChannel,
        value: Dict,
    ):
        super().__init__()
        self.channel_id: int = discord_channel.id
        self.value: Dict = value
        self.role_id: int = discord_role.id


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    value: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str | None] = mapped_column(default=None)


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
