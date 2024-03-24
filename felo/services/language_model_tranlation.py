import asyncio

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.models.lookup import Lookup
from felo.schemas.cards import (
    Card,
    CardTypesEnum,
    Explanation,
    NormalizedVersion,
    PossibleTranslation,
)
from felo.schemas.translations import (
    PhraseExtractionRequestToLM,
    LanguageModelEnum,
    TranslationRequest,
)
from felo.services.LanguageModelsAdapters.language_model_protocol import (
    LanguageModelApiAadapter,
)
from felo.services.LanguageModelsAdapters.openai import OpenaiApiAdapter
from felo.services.LanguageModelsAdapters.openai_adhoc import OpenaiAdhocApiAdapter
from felo.services.postprocessing import PostprocessingPipeline
from felo.services.preprocessing import preprocess

postprocessing = PostprocessingPipeline()


async def make_requests_to_adapter(
    session: AsyncSession,
    adapter: LanguageModelApiAadapter,
    translator_request: TranslationRequest,
) -> list[Card]:
    translate_coroutine = adapter.translate(translator_request)
    extract_coroutine = adapter.extract_phrases(translator_request)
    [translate_response, extract_response] = await asyncio.gather(
        translate_coroutine, extract_coroutine
    )
    logger.debug(f"translate_response: {translate_response}")
    logger.debug(f"extract_response: {extract_response}")

    source_translation = Card(
        text=translator_request.text,
        card_type=CardTypesEnum.SOURCE,
        text_translation=[
            PossibleTranslation(
                pos=None,
                translation=translation,
            )
            for translation in set(translate_response["translations"])
        ],
        normilized=(
            NormalizedVersion(
                normalized_text=translate_response["normalized_text"],
                normilized_text_translation=translate_response[
                    "normalized_text_translations"
                ],
            )
            if translate_response["normalized_text"]
            else None
        ),
    )

    extracted_phrases = [
        Card(
            text=r["phrase_text"],
            card_type=r["phrase_type"],
            text_translation=[
                PossibleTranslation(
                    pos=None,
                    translation=translation,
                )
                for translation in set(r["translations"])
            ],
            normilized=(
                NormalizedVersion(
                    normalized_text=r["normalized_phrase_text"],
                    normilized_text_translation=r["normalized_translations"],
                )
                if r["normalized_phrase_text"]
                else None
            ),
            explanation=Explanation(explanation_translation=r["explanation"]),
        )
        for r in extract_response
        if "phrase_type" in r and r["phrase_type"] in CardTypesEnum._member_names_
    ]
    return source_translation, extracted_phrases


API_ADAPTERS: dict[LanguageModelEnum, LanguageModelApiAadapter] = {
    LanguageModelEnum.OPENAI: OpenaiApiAdapter(),
    LanguageModelEnum.ADHOC_OPENAI: OpenaiAdhocApiAdapter(),
}

# def preprocess_translor_request(
#     translator_request: TranslationRequest,
# ) -> TranslationRequest:


async def language_model_translation(
    session: AsyncSession,
    translator_request: TranslationRequest,
    lookup: Lookup,
    language_model: LanguageModelEnum,
) -> list[Card]:
    api_adapter = API_ADAPTERS[language_model]
    # lm_request = TranslationRequest.from_translation_request(translator_request)

    translator_request = preprocess(language_model, translator_request)
    logger.debug(f"lm_request after pipeline {translator_request}")
    source_translation_card, extracted_phrases = await make_requests_to_adapter(
        session, api_adapter, translator_request
    )
    final_cards = postprocessing.process(
        source_translation=source_translation_card, extracted_phrases=extracted_phrases
    )
    logger.debug(f"final_cards {final_cards}")
    return final_cards
