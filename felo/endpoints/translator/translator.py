import uuid
from datetime import datetime

from fastapi import APIRouter, Body, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.connection.session import get_session
from felo.db.logic.lookup import get_or_create_lookup
from felo.db.models.lookup import Lookup
from felo.schemas.cards import Card
from felo.schemas.lookup import (
    FastTranslationResponseSchema,
    LangModelResponseSchema,
    LookupSchema,
)
from felo.schemas.translations import FastTranslationRequest, TranslationRequest
from felo.schemas.user import UserSchema
from felo.services.language_model_tranlation import (
    FastTranslatorEnum,
    LanguageModelEnum,
    language_model_translation,
)
from felo.services.simple_translation import google_translate

# from felo.services.google_translator import google_translsate
from felo.utils.jwt_utils import get_current_user

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


# @api_router.get("/deep/stream")
# def deep_translate_stream():
#     def event():
#         while True:
#             # HERE lies the question: wait for state to be update
#             for message in state.messages:
#                 yield "data: {}\n\n".format(json.dumps(message))

#     return StreamingResponse(event_stream(), media_type="text/event-stream")
