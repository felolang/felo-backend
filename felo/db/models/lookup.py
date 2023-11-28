# mypy: ignore-errors
import uuid
from enum import Enum
from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from felo.schemas.languages.iso639 import Language

from .base import BaseTable


class Lookup(BaseTable):
    __tablename__ = "lookup"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))

    source_language: Mapped[Language]
    target_language: Mapped[Language]
    user: Mapped[List["User"]] = relationship(back_populates="lookups")
    text: Mapped[str]  # TODO: define man_length
    context: Mapped[Optional[str]]  # TODO: define max_length
    context_translation: Mapped[Optional[str]]  # TODO: define max_length
    lookup_answers: Mapped[List["LookupAnswer"]] = relationship(
        back_populates="lookup", lazy="selectin"
    )


class TranslateEngineEnum(Enum):
    GOOGLE = "google"
    GPT_3_5_TURBO_1106 = "gpt_3_5_turbo_1106"


# class TranslateEngine(BaseTable):
#     __tablename__ = "translate_engine"
#     name: Mapped[TranslateEngineEnum]


class LookupAnswer(BaseTable):
    __tablename__ = "lookup_answer"

    lookup_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lookup.id"))
    lookup: Mapped[List["Lookup"]] = relationship(back_populates="lookup_answers")
    engine: Mapped[TranslateEngineEnum]
    text_translation: Mapped[str]  # TODO: define max_length
    normalized_text: Mapped[Optional[str]]  # TODO: define max_length
    normalized_text_translation: Mapped[Optional[str]]  # TODO: define max_length
    pos: Mapped[Optional[str]]  # TODO: define max_length
    phrases: Mapped[List["LookupPhrases"]] = relationship(
        back_populates="lookup_answer", lazy="selectin"
    )


class PhrasesTypeEnum(Enum):
    IDIOM = "IDIOM"
    SLANG = "SLANG"
    PHRASAL_VERB = "PHRASAL_VERB"
    NOTHING = "NOTHING"


class LookupPhrases(BaseTable):
    __tablename__ = "phrases"
    phrase_text: Mapped[str]  # TODO: define max_length
    phrase_normalized_text: Mapped[str]  # TODO: define max_length
    phrase_text_translation: Mapped[str]  # TODO: define max_length
    phrase_normalized_text_translation: Mapped[str]  # TODO: define max_length
    type: Mapped[PhrasesTypeEnum]
    lookup_answer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lookup_answer.id"))
    lookup_answer: Mapped[List["LookupAnswer"]] = relationship(back_populates="phrases")
    explanation: Mapped[Optional[str]]  # TODO: define max_length
    explanation_translation: Mapped[Optional[str]]  # TODO: define max_length
