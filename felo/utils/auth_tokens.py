from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.models.user import Token


class TokenSchema(BaseModel):
    token: str


async def add_blacklist_token(session: AsyncSession, token: TokenSchema):
    session.add(Token(token=token.token))
    await session.commit()
    return True


async def is_token_blacklisted(session: AsyncSession, token: TokenSchema):
    query = await session.execute(select(Token).filter_by(token=token.token))
    res = query.one_or_none()

    if not res:
        return False
    return True
