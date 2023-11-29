from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from felo.config.utils import CONFIG
from felo.db.connection.session import get_session
from felo.db.logic.user import get_user_by_email
from felo.db.models.user import User
from felo.schemas.user import UserSchema
from felo.utils.auth_tokens import TokenSchema, is_token_blacklisted

# Create a fake db:
FAKE_DB = {"din.latypov@gmail.com": {"name": "Guillermo Paoletti"}}


# Helper to read numbers using var envs
# def cast_to_number(id):
#     temp = os.environ.get(id)
#     if temp is not None:
#         try:
#             return float(temp)
#         except ValueError:
#             return None
#     return None


# Configuration
API_SECRET_KEY = CONFIG.SECRET_KEY
if API_SECRET_KEY is None:
    raise BaseException("Missing API_SECRET_KEY env var.")
API_ALGORITHM = CONFIG.ALGORITHM


# Token url (We should later create a token url that accepts just a user and a password to use swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


# Create token internal function
def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET_KEY, algorithm=API_ALGORITHM)
    return encoded_jwt


# Create token for an email
def create_token(email):
    access_token_expires = timedelta(minutes=CONFIG.API_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return access_token


def decode_token(token):
    return jwt.decode(token, API_SECRET_KEY, algorithms=[API_ALGORITHM])


def create_refresh_token(email):
    expires = timedelta(minutes=CONFIG.REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data={"sub": email}, expires_delta=expires)


async def get_current_user_token(
    session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)
):
    _ = await get_current_user(session, token)
    return token


async def get_current_user_optionally(
    session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    logger.debug(f"token {token}")
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        logger.debug(f"payload {payload}")
        if email is None:
            raise CREDENTIALS_EXCEPTION
    except jwt.PyJWTError:
        return None

    if user_db := await get_user_by_email(session, email):
        return user_db

    return None


async def get_current_user(
    session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> User:
    if await is_token_blacklisted(session, TokenSchema(token=token)):
        raise CREDENTIALS_EXCEPTION
    logger.debug(f"token {token}")
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        logger.debug(f"payload {payload}")
        if email is None:
            raise CREDENTIALS_EXCEPTION
    except jwt.PyJWTError:
        raise CREDENTIALS_EXCEPTION

    if user_db := await get_user_by_email(session, email):
        return user_db

    raise CREDENTIALS_EXCEPTION
