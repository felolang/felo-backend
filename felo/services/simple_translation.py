import datetime

from google.cloud import translate_v3
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from felo.config.utils import CONFIG
from felo.db.models.lookup import Lookup
from felo.schemas.cards import Card, CardTypesEnum
from felo.schemas.lookup import LookupSchema
from felo.schemas.translations import FastTranslationRequest
from felo.services.language_model_tranlation import FastTranslatorEnum


# Initialize Translation client
async def google_translate(
    session: AsyncSession,
    translator_request: FastTranslationRequest,
    lookup: Lookup,
    translator: FastTranslatorEnum,
) -> list[Card]:
    """Translating Text."""
    google_translator_client = translate_v3.TranslationServiceAsyncClient()

    start = datetime.datetime.now()
    logger.debug(f"Time 1: {datetime.datetime.now() - start}")

    location = "global"

    parent = f"projects/{CONFIG.PROJECT_ID}/locations/{location}"

    request = translate_v3.TranslateTextRequest(
        parent=parent,
        contents=[translator_request.text],
        mime_type="text/plain",  # mime types: text/plain, text/html
        source_language_code=translator_request.source_language.value,
        target_language_code=translator_request.target_language.value,
    )
    logger.debug(f"Time 2: {datetime.datetime.now() - start}")

    response = await google_translator_client.translate_text(request=request)
    logger.debug(f"Time 3: {datetime.datetime.now() - start}")

    translation = response.translations[0]
    logger.debug(f"Time taken: {datetime.datetime.now() - start}")

    return [
        Card(
            text=translator_request.text,
            card_type=CardTypesEnum.SOURCE,
            text_translation=[
                {"translation": translation.translated_text, "pos": None}
            ],
            normilized=None,
            explanation=None,
        )
    ]
