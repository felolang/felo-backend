import uuid
from datetime import datetime

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.connection.session import get_session
from felo.db.models.lookup import Lookup
from felo.schemas.cards import Card
from felo.schemas.lookup import LookupSchema
from felo.schemas.translations import (
    FastTranslationRequest,
    FastTranslatorEnum,
    TranslationRequest,
)
from felo.services.language_model_tranlation import (
    LanguageModelEnum,
    language_model_translation,
)
from felo.services.simple_translation import google_translate

# from felo.services.google_translator import google_translsate

api_router = APIRouter(
    prefix="/translations",
    tags=["Translator"],
)


def mock_lookup(translator_request: TranslationRequest = Body(...)):
    return LookupSchema(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        create_time=datetime.now(),
        update_time=datetime.now(),
        lookup_answers=[],
        source_language="EN",
        target_language="RU",
        text=translator_request.text,
        context=translator_request.context,
    )


@api_router.post("/lm/{language_model_type}", response_model=list[Card])
async def translate_with_language_model(
    language_model_type: LanguageModelEnum,
    session: AsyncSession = Depends(get_session),
    translator_request: TranslationRequest = Body(...),
    # lookup: Lookup = Depends(get_or_create_lookup),
    lookup: Lookup = Depends(mock_lookup),
):
    res = await language_model_translation(
        session, translator_request, lookup, language_model_type
    )
    return res


@api_router.post("/fast/{translator}", response_model=list[Card])
async def translate_with_fast_translator(
    translator: FastTranslatorEnum,
    session: AsyncSession = Depends(get_session),
    translator_request: FastTranslationRequest = Body(...),
    # lookup: Lookup = Depends(get_or_create_lookup),
):
    lookup = None
    res = await google_translate(session, translator_request, lookup, translator)
    return res
