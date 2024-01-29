import uuid
from typing import List, Optional

import inflect
from loguru import logger
from pydantic import BaseModel, Field, constr

from felo.config.utils import CONFIG
from felo.schemas.languages.iso639 import Language

p = inflect.engine()


class TranslationRequest(BaseModel):
    id: uuid.UUID = Field(alias="lookup_id")
    text: str = Field(
        alias="input_text", max_length=CONFIG.LANGUAGE_MODEL_TEXT_MAX_LENGTH
    )
    context: str = Field(max_length=CONFIG.LANGUAGE_MODEL_CONTEXT_MAX_LENGTH)
    source_language: Language
    target_language: Language
    text_start_position: int

    class Config:
        populate_by_name = True


def find_nth(haystack: str, needle: str, n: int) -> int:
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


def rfind_nth(haystack: str, needle: str, n: int) -> int:
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


class PhraseExtractionRequestToLM(BaseModel):
    id: uuid.UUID = Field(alias="lookup_id")
    context: str = Field(max_length=CONFIG.LANGUAGE_MODEL_CONTEXT_MAX_LENGTH)
    source_language: Language
    target_language: Language


class TranslationRequestToLM(BaseModel):
    id: uuid.UUID = Field(alias="lookup_id")
    text: str = Field(
        alias="input_text", max_length=CONFIG.LANGUAGE_MODEL_TEXT_MAX_LENGTH
    )
    start_position: int
    context: str = Field(max_length=CONFIG.LANGUAGE_MODEL_CONTEXT_MAX_LENGTH)
    small_context: str = Field(max_length=CONFIG.LANGUAGE_MODEL_CONTEXT_MAX_LENGTH)
    source_language: Language
    target_language: Language

    class Config:
        populate_by_name = True

    @classmethod
    def retrieve_small_context(
        cls, text: str, context: str, text_start_position: int
    ) -> str:
        res_list = []
        context_window = 2
        left_part = context[:text_start_position].strip()
        right_part = context[text_start_position + len(text) :].strip()

        left_part_splitted = left_part.split()
        right_part_splitted = right_part.split()

        res_list.extend(left_part_splitted[-context_window:])
        res_list.append(text)
        res_list.extend(right_part_splitted[:context_window])
        # small_context_left = left_part.rfind(" ")
        # small_context_right = right_part.find(" ") + text_start_position + len(text)
        # if small_context_left == -1:
        #     small_context_left = text_start_position - len(left_part)
        # if small_context_right == -1:
        #     small_context_right = text_start_position + len(text)
        # logger.debug(
        #     f"retrieve_small_context {left_part} {right_part} {small_context_left} {small_context_right}"
        # )
        return " ".join(res_list)

    @classmethod
    def from_translation_request(
        cls, translation_request: TranslationRequest
    ) -> "TranslationRequestToLM":
        request_to_lm = TranslationRequestToLM(
            id=translation_request.id,
            text=translation_request.text,
            context=translation_request.context,
            source_language=translation_request.source_language.value,
            target_language=translation_request.target_language.value,
            small_context=cls.retrieve_small_context(
                translation_request.text,
                translation_request.context,
                translation_request.text_start_position,
            ),
            start_position=translation_request.text_start_position,
        )
        logger.debug(f"request_to_lm: {request_to_lm.small_context}")
        return request_to_lm


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
    text: constr(max_length=CONFIG.FAST_TRANSLATION_MAX_LENGTH)
    source_language: Language
    target_language: Language


# class FastTranslationResponse(BaseModel):
#     selected_text_translation: List[str]
#     source_language: Language
#     target_language: Language
