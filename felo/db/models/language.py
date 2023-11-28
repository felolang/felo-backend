from sqlalchemy import String
from sqlalchemy.orm import mapped_column

from .base import BaseTable


class Language(BaseTable):
    __tablename__ = "language"

    iso639_1 = mapped_column(
        String(2),
        nullable=False,
        unique=True,
        index=True,
    )
