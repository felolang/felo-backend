import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

from felo.db.models.lookup import PhrasesTypeEnum, TranslateEngineEnum
from felo.schemas.base_model_db import BaseModelDB
from felo.schemas.languages.iso639 import Language


class PhrasesSchema(BaseModelDB):
    phrase_text: str
    phrase_normalized_text: str
    phrase_text_translation: str
    phrase_normalized_text_translation: str
    type: PhrasesTypeEnum
    lookup_answer_id: Optional[uuid.UUID] = None
    explanation: Optional[str] = None
    explanation_translation: Optional[str] = None


class LookupAnswerSchema(BaseModelDB):
    lookup_id: uuid.UUID
    engine: TranslateEngineEnum
    text_translation: str
    normalized_text: Optional[str] = None
    normalized_text_translation: Optional[str] = None
    pos: Optional[str] = None

    # phrases: List[PhrasesSchema]


class LookupSchema(BaseModelDB):
    context_translation: Optional[str] = None
    user_id: uuid.UUID
    source_language: Language
    target_language: Language
    text: str
    context: Optional[str] = None
    lookup_answers: List[LookupAnswerSchema]


class LangModelResponseSchema(BaseModel):
    context_translation: Optional[str] = None
    source_language: Language
    target_language: Language
    # engine: TranslateEngineEnum
    text_translation: str
    normalized_text: Optional[str] = Field(
        default=None,
        description="normalized version of 'text' if it is single word, else None",
    )
    normalized_text_translation: Optional[str] = Field(
        default=None,
        description="translation of 'normalized_text'",
    )
    pos: Optional[str] = Field(
        default=None,
        description="part of speech of 'text' if it is single word, else None",
    )
    phrases: List[PhrasesSchema] = Field(
        default=[],
        description="constructions founded in 'text' related to 'context'",
    )


class SimpleTranslationResponseSchema(BaseModel):
    source_language: Language
    target_language: Language
    # engine: TranslateEngineEnum
    text_translation: str
