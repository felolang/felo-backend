from fastapi import APIRouter, Body, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.connection.session import get_session
from felo.db.logic.lookup import get_or_create_lookup
from felo.db.models.lookup import Lookup
from felo.schemas.lookup import LangModelResponseSchema
from felo.schemas.translations import TranslationRequest
from felo.schemas.user import UserSchema
from felo.services.language_model_tranlation import (
    LanguageModelEnum,
    language_model_translation,
)

# from felo.services.google_translator import google_translsate
from felo.utils.jwt_utils import get_current_user

api_router = APIRouter(
    prefix="/translations",
    tags=["Translator"],
)


@api_router.post("/lm/{language_model_type}", response_model=LangModelResponseSchema)
async def translate_with_language_model(
    language_model_type: LanguageModelEnum,
    session: AsyncSession = Depends(get_session),
    translator_request: TranslationRequest = Body(...),
    lookup: Lookup = Depends(get_or_create_lookup),
):
    res = await language_model_translation(
        session, translator_request, lookup, language_model_type
    )
    return res


# @api_router.get("/deep/stream")
# def deep_translate_stream():
#     def event():
#         while True:
#             # HERE lies the question: wait for state to be update
#             for message in state.messages:
#                 yield "data: {}\n\n".format(json.dumps(message))

#     return StreamingResponse(event_stream(), media_type="text/event-stream")


@api_router.get("/protected")
def test2(current_email: str = Depends(get_current_user)):
    return {"message": "protected api_app endpoint"}


# @api_router.post("/google", response_model=LookupSchema)
# async def fast_google_translate(translator_request: FastTranslationRequest = Body(...)):
#     res = await google_translate(translator_request)
#     return res
