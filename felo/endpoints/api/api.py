from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from felo.db.connection.session import get_session
from felo.db.models.user import User
from felo.utils.jwt_utils import get_current_user

api_router = APIRouter(
    prefix="/api",
    tags=["Api endpints"],
)


@api_router.get("/")
async def test():
    return {"message": "unprotected api_app endpoint"}


@api_router.get("/protected")
async def test2(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return {"message": "protected api_app endpoint"}
