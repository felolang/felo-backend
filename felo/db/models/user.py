from __future__ import annotations

from typing import List

from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseTable


class User(BaseTable):
    __tablename__ = "user"

    username = mapped_column(
        "username",
        TEXT,
        nullable=True,
        unique=True,
        index=True,
        doc="Username for authentication.",
    )
    password = mapped_column(
        "password",
        TEXT,
        nullable=True,
        index=True,
        doc="Hashed password.",
    )
    email = mapped_column(
        "email",
        TEXT,
        nullable=False,
        doc="Email for notifications.",
    )
    lookups: Mapped[List["Lookup"]] = relationship(back_populates="user")


class Token(BaseTable):
    __tablename__ = "token"

    token = mapped_column(
        "token",
        TEXT,
        nullable=False,
        unique=True,
        index=True,
        doc="Username for authentication.",
    )
