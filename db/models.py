from __future__ import annotations

from typing import List, Optional
from typing_extensions import Annotated
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Date,
    SmallInteger,
    BigInteger,
    select,
    Table,
    Sequence,
    Identity
)

from sqlalchemy.types import VARCHAR

from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    Mapped,
    mapped_column,
    MappedAsDataclass,
    object_session,
)
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)


class Base(AsyncAttrs, DeclarativeBase, MappedAsDataclass):
    pass


discord_id_pk = Annotated[int, mapped_column(BigInteger, primary_key=True)]
region_int_pk = Annotated[int, mapped_column(Identity(), primary_key=True)]
name_str = Annotated[str, mapped_column(String)]
message_len = Annotated[int, mapped_column(SmallInteger)]
discord_date = Annotated[datetime, mapped_column(Date)]
guild_fk = Annotated[int, mapped_column(ForeignKey("guilds.id"))]
role_fk = Annotated[int, mapped_column(ForeignKey("roles.id"))]


class Guild(Base):
    __tablename__ = "guilds"

    # Attributes
    id: Mapped[discord_id_pk]
    name: Mapped[name_str]

    # Bidirectional One-To-Many Relationships
    roles: Mapped[List[Role]] = relationship(
        default_factory=list)


class Role(Base):
    __tablename__ = 'roles'

    # Attributes
    id: Mapped[discord_id_pk]
    name: Mapped[name_str]
    guild_id: Mapped[guild_fk]

    region: Mapped[Optional[Region]] = relationship(
        default=None,
        back_populates="role"
    )
    is_active: Mapped[bool] = mapped_column(default=True)


class Region(Base):
    __tablename__ = 'regions'

    id: Mapped[region_int_pk]
    name: Mapped[name_str]

    role_id: Mapped[role_fk]
    role: Mapped[Role] = relationship(back_populates="region")