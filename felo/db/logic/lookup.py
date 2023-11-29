import uuid

from fastapi import Body, Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload

from felo.db.connection.session import get_session
from felo.db.models.lookup import Lookup, LookupAnswer
from felo.db.models.user import User
from felo.schemas.translations import TranslationRequest

# from felo.services.google_translator import google_translsate
from felo.utils.jwt_utils import get_current_user, get_current_user_optionally


async def get_lookup_selectinload(
    session: AsyncSession, lookup_id: uuid.UUID
) -> Lookup | None:
    query = (
        select(Lookup)
        # .options(selectinload(Lookup.lookup_answers))
        # .options(
        #     subqueryload(Lookup.lookup_answers).subqueryload(LookupAnswer.phrases)
        # )
        .where(Lookup.id == lookup_id)
    )
    res = await session.execute(query)
    lookup_db = res.scalars().first()
    return lookup_db


async def get_or_create_lookup(
    session: AsyncSession = Depends(get_session),
    translator_request: TranslationRequest = Body(...),
    user: User | None = Depends(get_current_user_optionally),
) -> Lookup:
    logger.debug(f"get_or_create_lookup: {translator_request}")
    # lookup_db = await session.get(Lookup, translator_request.id)
    lookup_db = await get_lookup_selectinload(session, translator_request.id)
    if not lookup_db:
        lookup_db = Lookup(
            **translator_request.model_dump(),
            user_id=user.id if user is not None else None,
        )
        session.add(lookup_db)
        await session.commit()
        lookup_db = await get_lookup_selectinload(session, translator_request.id)

    logger.debug(f"get_or_create_lookup: {type(lookup_db)} {lookup_db.__dict__}")
    assert lookup_db is not None
    return lookup_db
