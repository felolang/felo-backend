from typing import Optional, Protocol

from felo.schemas.translations import PhraseExtractionRequestToLM, TranslationRequest


class LanguageModelApiAadapter(Protocol):
    async def translate(self, translator_request: TranslationRequest) -> dict:
        ...

    async def extract_phrases(self, translator_request: TranslationRequest) -> dict:
        ...

    def get_engine(self) -> str:
        ...
