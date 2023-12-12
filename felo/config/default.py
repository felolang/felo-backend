# mypy: ignore-errors
from os import environ

from google.cloud import secretmanager
from loguru import logger
from pydantic_settings import BaseSettings

ENV = environ.get("ENV", "dev")
CONFIG_PATH_PREFIX = (
    "../config/"
    if environ.get("ALEMBIC_MIGRATIONS", None) is not None
    else "felo/config/"
)
dotenv_file = f"{CONFIG_PATH_PREFIX}{ENV}.env"
logger.debug(f"dotenv_file {dotenv_file}")


def access_secret_version(secret_id, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/named-mason-400816/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode("UTF-8")


def load_env_string(env_string):
    for line in env_string.split("\n"):
        line = line.strip()
        if line and "=" in line:
            key, value = line.split("=")
            environ[key] = value


if ENV == "prod":
    secret_envs = access_secret_version("SECRET_ENVS")
    # logger.debug(f"secret_envs {secret_envs}")
else:
    with open(f"{CONFIG_PATH_PREFIX}secret.env", "r", encoding="utf-8") as f:
        secret_envs = f.read()
# logger.debug(f"secret_envs {secret_envs}")
load_env_string(secret_envs)


class DefaultSettings(BaseSettings):
    ENV: str = environ.get("ENV", "dev")
    GOOGLE_CLIENT_ID: str = environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = environ.get("GOOGLE_CLIENT_SECRET")
    PROJECT_ID: str
    PATH_PREFIX: str = "/api/v1"
    SECRET_KEY: str = environ.get("SECRET_KEY")
    ALGORITHM: str = environ.get("ALGORITHM", "HS256")
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        environ.get("API_ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    )
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(
        environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 30)  # 30 days
    )

    SQL_CLOUD_INSTANCE_CONNECTION_NAME: str | None = environ.get(
        "SQL_CLOUD_INSTANCE_CONNECTION_NAME", None
    )
    POSTGRES_DB: str = "main"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_USER: str = "user"
    POSTGRES_PORT: str = "5432"
    POSTGRES_PASSWORD: str = "hackme"
    DB_CONNECT_RETRY: int = 20
    DB_POOL_SIZE: int = 15

    LANGUAGE_MODEL_TEXT_MAX_LENGTH: int = 500
    LANGUAGE_MODEL_CONTEXT_MAX_LENGTH: int = 1000

    FAST_TRANSLATION_MAX_LENGTH: int = 2000

    FRONTEND_URL: str = "http://127.0.0.1:8000"

    @property
    def database_settings(self) -> dict:
        """
        Get all settings for connection with database.
        """
        return {
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        db_uri = (
            "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
                **self.database_settings,
            )
        )
        # logger.debug(f"Database uri: {db_uri}")
        return db_uri

    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    # @model_validator(mode="before")
    # @classmethod
    # def extract_secrets_from_manager(cls, data: dict) -> dict:

    #     return data

    class Config:
        env_file = dotenv_file
        env_file_encoding = "utf-8"
