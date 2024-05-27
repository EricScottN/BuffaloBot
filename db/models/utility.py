"""
All SQLAlchemy related model setup
"""

from __future__ import annotations

from typing import List

from sqlalchemy import (
    SmallInteger,
    BigInteger,
    Identity,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column,
)
from typing_extensions import Annotated

from db.models import Base

region_int_pk = Annotated[int, mapped_column(Identity(), primary_key=True)]
message_len = Annotated[int, mapped_column(SmallInteger)]


class Region(Base):
    __tablename__ = "region"

    # Attributes
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="region", default=None)

    def __repr__(self) -> str:
        return f"{self.name}"


class RoleGroup(Base):
    __tablename__ = "role_group"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str]
    permission_value: Mapped[int] = mapped_column(BigInteger)

    roles: Mapped[List["Role"]] = relationship(
        back_populates="role_group", default_factory=list
    )

    __table_args__ = (
        UniqueConstraint("name", "permission_value", name="name_permissions_key"),
    )


class WordEmoji(Base):
    __tablename__ = "word_emoji"

    word: Mapped[str] = mapped_column(primary_key=True)
    emoji: Mapped[str] = mapped_column(primary_key=True)
