import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, constr

from felo.config.utils import CONFIG
from felo.schemas.languages.iso639 import Language


class TranslationRequest(BaseModel):
    id: uuid.UUID = Field(alias="lookup_id")
    text: str = Field(alias="input_text")
    context: str
    source_language: Language
    target_language: Language

    class Config:
        populate_by_name = True


# class Phrase(BaseModel):
#     phrase: str
#     phrase_translation: List[str]
#     type_of_phrase: str


# class TranslationResponse(BaseModel):
#     selected_text_translation: constr(max_length=CONFIG.DEEP_TRANSLATION_MAX_LENGTH)
#     phrases: List[Phrase]
#     part_of_speech: Optional[str]
#     normal_form: Optional[str]
#     normal_form_translation: List[str]
#     source_language: Language
#     target_language: Language


class FastTranslationRequest(BaseModel):
    selected_text: constr(max_length=CONFIG.FAST_TRANSLATION_MAX_LENGTH)
    source_language: Language
    target_language: Language


# class FastTranslationResponse(BaseModel):
#     selected_text_translation: List[str]
#     source_language: Language
#     target_language: Language
