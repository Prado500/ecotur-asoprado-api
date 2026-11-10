"""Application settings, read once from the process environment and the repository .env file.

Every configuration value of the app lives here (ADR-0013). Values are validated when first read,
so a missing or malformed variable stops the app at startup with an error that names the field. The
HTTP layer injects them with ``Depends(get_settings)``; code with no request calls
``get_settings()`` directly.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository-root .env, located by this file and not by the working directory. Optional:
# process environment variables take priority over it.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class DatabaseSettings(BaseSettings):
    """Settings the database layer needs, and the only ones database migrations need.

    Kept apart so that ``alembic upgrade`` runs with the database URL alone, as the CD pipeline
    does.

    Attributes:
        database_url: SQLAlchemy async URL. Required, non-empty.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    database_url: str = Field(min_length=1)


class Settings(DatabaseSettings):
    """Whole application configuration: one field per environment variable, named in upper case.

    Required (no default, non-empty): jwt_secret_key, mail_username, mail_password,
    azure_storage_connection_string and the inherited database_url. The rest keep the defaults
    the app had before this module existed.
    """

    jwt_secret_key: str = Field(min_length=1)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    verification_token_expire_minutes: int = 15

    mail_username: str = Field(min_length=1)
    mail_password: str = Field(min_length=1)
    mail_from: str | None = None
    mail_port: int = 465
    mail_server: str = "smtp.gmail.com"

    azure_storage_connection_string: str = Field(min_length=1)
    azure_container_name: str = "ecotur-images"
    azure_temporal_container_name: str = "temp-ecotur-images"

    frontend_url: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:3000"

    @property
    def mail_sender(self) -> str:
        """Sender address: mail_from when set, otherwise the SMTP account (mail_username).

        Returns:
            str: The address the verification email is sent from.
        """
        return self.mail_from or self.mail_username


@lru_cache
def get_settings() -> Settings:
    """Builds the application settings once and returns the same instance afterwards.

    Returns:
        Settings: The validated configuration.

    Raises:
        pydantic.ValidationError: When a required variable is missing or a value is malformed.
    """
    return Settings()


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Builds the database settings once; used by the engine and by Alembic.

    Returns:
        DatabaseSettings: The validated database configuration.

    Raises:
        pydantic.ValidationError: When the database URL is missing or empty.
    """
    return DatabaseSettings()
