import os
from datetime import datetime

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from felo.config.utils import CONFIG
from felo.db.connection.session import get_session
from felo.db.logic.user import get_user_by_email, validate_or_create_user
from felo.utils.auth_tokens import TokenSchema, add_blacklist_token
from felo.utils.jwt_utils import (
    CREDENTIALS_EXCEPTION,
    create_refresh_token,
    create_token,
    decode_token,
    get_current_user_token,
)

auth_app = FastAPI()

# OAuth settings
GOOGLE_CLIENT_ID = CONFIG.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = CONFIG.GOOGLE_CLIENT_SECRET
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException("Missing env variables")

# Set up OAuth
config_data = {
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Set up the middleware to read the request session
SECRET_KEY = os.environ.get("SECRET_KEY") or None
auth_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@auth_app.get("/")
def test():
    return JSONResponse({"message": "auth_app"})


FRONTEND_URL = os.environ.get("FRONTEND_URL") or "http://127.0.0.1:8000/main"


@auth_app.route("/login")
async def login(request: Request):
    redirect_uri = FRONTEND_URL
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_app.post("/token")
async def auth(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        logger.debug(f"request {request.url}")
        access_token = await oauth.google.authorize_access_token(request)
        logger.debug(f"access_token {access_token} {type}")
    except OAuthError as e:
        logger.error(f"{e}")
        raise CREDENTIALS_EXCEPTION
    user_data = access_token["userinfo"]
    logger.debug(f"user_data {user_data}")
    if await validate_or_create_user(session, user_data["email"]):
        return JSONResponse(
            {
                "result": True,
                "access_token": create_token(user_data["email"]),
                "refresh_token": create_refresh_token(user_data["email"]),
            }
        )
    raise CREDENTIALS_EXCEPTION


@auth_app.get("/logout")
async def logout(
    token: str = Depends(get_current_user_token),
    session: AsyncSession = Depends(get_session),
):
    if await add_blacklist_token(session, TokenSchema(token=token)):
        return JSONResponse({"result": True})
    raise CREDENTIALS_EXCEPTION


@auth_app.post("/refresh")
async def refresh(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        # Only accept post requests
        if request.method == "POST":
            form = await request.json()
            if form.get("grant_type") == "refresh_token":
                token = form.get("refresh_token")
                payload = decode_token(token)
                # Check if token is not expired
                if datetime.utcfromtimestamp(payload.get("exp")) > datetime.utcnow():
                    email = payload.get("sub")
                    # Validate email
                    if get_user_by_email(session, email):
                        # Create and return token
                        return JSONResponse(
                            {"result": True, "access_token": create_token(email)}
                        )

    except Exception:
        raise CREDENTIALS_EXCEPTION
    raise CREDENTIALS_EXCEPTION


# @api_router.route("/logout")
# async def logout(request: Request):
#     request.session.pop("user", None)
#     return RedirectResponse(url="/")
