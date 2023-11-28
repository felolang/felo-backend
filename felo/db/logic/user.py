from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.models.user import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    user_db = await session.scalar(query)
    return user_db


async def validate_or_create_user(session: AsyncSession, email: str) -> User | None:
    user_db = await get_user_by_email(session, email)

    if not user_db:
        user_db = User(email=email)
        session.add(user_db)
        await session.commit()

    return user_db
