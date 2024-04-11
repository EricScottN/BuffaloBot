from typing import List, Optional
from typing_extensions import Annotated
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Date,
    BigInteger,
    select,
    Table,
    Sequence
)

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


# Many-To-Many Association Tables

guilds_members = Table(
    "guilds_members",
    Base.metadata,
    Column("guild_id", ForeignKey("guilds.id"), primary_key=True),
    Column("member_id", ForeignKey("members.id"), primary_key=True)
)

roles_members = Table(
    "roles_members",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("member_id", ForeignKey("members.id"), primary_key=True)
)

intpk = Annotated[int, mapped_column(BigInteger, primary_key=True, nullable=False)]
name_str = Annotated[str, mapped_column(String)]
guild_fk = Annotated[int, mapped_column(ForeignKey("guilds.id"))]


class Guild(Base):
    __tablename__ = "guilds"

    # Attributes
    id: Mapped[intpk]
    name: Mapped[name_str]

    # Bidirectional One-To-Many Relationships
    roles: Mapped[List["Role"]] = relationship(back_populates="guild")
    channels: Mapped[List["Channel"]] = relationship(back_populates="guild")
    categories: Mapped[List["Category"]] = relationship(back_populates="guild")

    # Bidirectional Many-To-Many Relationships
    members: Mapped[List["Member"]] = relationship(
        secondary=guilds_members,
        back_populates="guilds"
    )


class Role(Base):
    __tablename__ = 'roles'

    # Attributes
    id: Mapped[intpk]
    name: Mapped[name_str]

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="roles")

    # Bidirectional Many-To-Many Relationships
    members: Mapped[List["Member"]] = relationship(
        secondary=roles_members,
        back_populates="roles"
    )


class Member(Base):
    __tablename__ = 'members'

    # Attributes
    id: Mapped[intpk]
    name: Mapped[name_str]

    # Bidirectional Many-To-Many Relationships
    guilds: Mapped[List["Guild"]] = relationship(
        secondary=guilds_members,
        back_populates="members"
    )
    roles: Mapped[Optional[List["Role"]]] = relationship(
        secondary=roles_members,
        back_populates="members")


class Channel(Base):
    __tablename__ = "channels"

    # Attributes
    id: Mapped[intpk]
    name: Mapped[name_str]

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="channels")
    category: Mapped[Optional["Category"]] = relationship(back_populates="channels")


class Category(Base):
    __tablename__ = "categories"

    # Attributes
    id: Mapped[intpk]
    name: Mapped[name_str]

    # Relationships
    guild: Mapped["Guild"] = relationship(back_populates="categories")
    channels: Mapped[Optional[List["Channel"]]] = relationship(back_populates="channels")

