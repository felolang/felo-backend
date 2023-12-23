import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PossibleTranslation(BaseModel):
    translation: str  # один из возможных переводов
    pos: Optional[
        str
    ]  # часть речи этого варианта перевода, если это одно слово. Если предложение - None


class NormalizedVersion(BaseModel):
    normalized_text: str
    normilized_text_translation: list[PossibleTranslation]


class Explanation(BaseModel):
    explanation: str
    explanation_translation: str


class CardTypesEnum(str, Enum):
    IDIOM = "IDIOM"
    SLANG = "SLANG"
    PHRASAL_VERB = "PHRASAL_VERB"
    ORDINARY_WORD = "ORDINARY_WORD"
    TERM = "TERM"
    SOURCE = "SOURCE"


class Card(BaseModel):
    id: Optional[uuid.UUID] = None  # для сохранения в избранное
    text: str
    card_type: CardTypesEnum
    text_translation: list[PossibleTranslation]
    normilized: Optional[
        NormalizedVersion
    ] = None  # если возможна нормализованная версия
    explanation: Optional[Explanation] = None  # если требуются объяснения к text
