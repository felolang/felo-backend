from fastapi import APIRouter, Body, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.connection.session import get_session
from felo.db.logic.lookup import get_lookup_by_id
from felo.db.models.lookup import Lookup
from felo.schemas.lookup import FastTranslationResponseSchema, LangModelResponseSchema
from felo.schemas.translations import TranslationRequest
from felo.schemas.user import UserSchema
from felo.services.favorites import save_lookup_to_favorites
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


@api_router.post("/favorites/{lookup_id}")
async def translate_with_language_model(
    session: AsyncSession = Depends(get_session),
    lookup: Lookup = Depends(get_lookup_by_id),
):
    res = await save_lookup_to_favorites()
