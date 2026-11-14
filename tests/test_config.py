"""
Tests for the application settings (app/core/config.py, ADR-0013).

Each test builds its environment with monkeypatch only and reads it with
``Settings(_env_file=None)``, so no developer .env file takes part unless the test
passes its own file.
"""

import runpy
from collections.abc import Callable
from pathlib import Path

import pytest
from dotenv import dotenv_values
from pydantic import ValidationError

from app.core.config import (
    ENV_FILE,
    DatabaseSettings,
    Settings,
    SuperadminBootstrapSettings,
    get_database_settings,
    get_settings,
)
from app.schemas.user import UserCreateByAdmin, UserRole

REQUIRED = (
    "database_url",
    "jwt_secret_key",
    "mail_username",
    "mail_password",
    "azure_storage_connection_string",
)

OPTIONAL_DEFAULTS = {
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "verification_token_expire_minutes": 15,
    "mail_from": None,
    "mail_port": 465,
    "mail_server": "smtp.gmail.com",
    "azure_container_name": "ecotur-images",
    "azure_temporal_container_name": "temp-ecotur-images",
    "frontend_url": "http://localhost:3000",
    "cors_origins": "http://localhost:3000",
}

ALL_FIELDS = (*REQUIRED, *OPTIONAL_DEFAULTS)

ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"
ROOT_CONFTEST = Path(__file__).resolve().parents[1] / "conftest.py"

VALID_REQUIRED = {
    "database_url": "sqlite+aiosqlite:///:memory:",
    "jwt_secret_key": "config-test-jwt-key",
    "mail_username": "smtp-account@test.com",
    "mail_password": "config-test-mail-password",
    "azure_storage_connection_string": "UseDevelopmentStorage=true",
}

BOOTSTRAP_VALUES = {
    "database_url": "sqlite+aiosqlite:///:memory:",
    "superadmin_cedula": "900000001",
    "superadmin_email": "root@test.com",
    "superadmin_first_name": "Ana",
    "superadmin_last_name": "Diaz",
    "superadmin_password": "Bootstrap-sentinel-1",
}


def _set_required(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gives every required setting a valid value in the process environment."""
    for name, value in VALID_REQUIRED.items():
        monkeypatch.setenv(name.upper(), value)


def _set_bootstrap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gives every bootstrap credential, and the database URL, a valid value."""
    for name, value in BOOTSTRAP_VALUES.items():
        monkeypatch.setenv(name.upper(), value)


def _clear(monkeypatch: pytest.MonkeyPatch, names: tuple[str, ...]) -> None:
    """Removes the given settings from the process environment."""
    for name in names:
        monkeypatch.delenv(name.upper(), raising=False)


@pytest.mark.parametrize("field", REQUIRED)
def test_missing_required_variable_fails_naming_it(
    monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    """Unhappy path: a missing required variable fails with one error that names its field."""
    _set_required(monkeypatch)
    monkeypatch.delenv(field.upper())

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert [(e["type"], e["loc"]) for e in exc_info.value.errors()] == [("missing", (field,))]


@pytest.mark.parametrize("field", REQUIRED)
def test_empty_required_variable_is_rejected(monkeypatch: pytest.MonkeyPatch, field: str) -> None:
    """Edge case: an empty required variable is rejected instead of passing as a value."""
    _set_required(monkeypatch)
    monkeypatch.setenv(field.upper(), "")

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert [(e["type"], e["loc"]) for e in exc_info.value.errors()] == [
        ("string_too_short", (field,))
    ]


def test_optional_variables_keep_their_current_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Happy path: without the optional variables, each field keeps the app's former default."""
    _set_required(monkeypatch)
    _clear(monkeypatch, tuple(OPTIONAL_DEFAULTS))

    settings = Settings(_env_file=None)

    assert set(Settings.model_fields) == set(REQUIRED) | set(OPTIONAL_DEFAULTS)
    assert {n: getattr(settings, n) for n in OPTIONAL_DEFAULTS} == OPTIONAL_DEFAULTS


def test_mail_sender_defaults_to_mail_username(monkeypatch: pytest.MonkeyPatch) -> None:
    """Edge case: with no mail_from, the sender is the SMTP account."""
    _set_required(monkeypatch)
    monkeypatch.setenv("MAIL_USERNAME", "account@test.com")
    monkeypatch.delenv("MAIL_FROM", raising=False)

    assert Settings(_env_file=None).mail_sender == "account@test.com"


def test_mail_sender_is_mail_from_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """Happy path: mail_from, when set, is the sender."""
    _set_required(monkeypatch)
    monkeypatch.setenv("MAIL_USERNAME", "account@test.com")
    monkeypatch.setenv("MAIL_FROM", "sender@test.com")

    assert Settings(_env_file=None).mail_sender == "sender@test.com"


def test_env_file_ignores_unknown_keys_and_expands_references(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Edge case: the repository .env shape (extra keys, ${VAR} references) is read as is."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "POSTGRES_USER=u\n"
        "POSTGRES_PASSWORD=p\n"
        "POSTGRES_HOST=h\n"
        "POSTGRES_PORT=5432\n"
        "POSTGRES_DB=d\n"
        "DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}"
        "@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}\n",
        encoding="utf-8",
    )
    _set_required(monkeypatch)
    monkeypatch.delenv("DATABASE_URL")

    settings = Settings(_env_file=env_file)

    assert settings.database_url == "postgresql+asyncpg://u:p@h:5432/d"


def test_process_environment_beats_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Edge case: a process environment variable takes priority over the same key in the file."""
    env_file = tmp_path / ".env"
    env_file.write_text("JWT_SECRET_KEY=from-file-key\n", encoding="utf-8")
    _set_required(monkeypatch)
    monkeypatch.setenv("JWT_SECRET_KEY", "from-process-key")

    assert Settings(_env_file=env_file).jwt_secret_key == "from-process-key"


def test_database_settings_need_only_the_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Happy path: migrations read the database URL alone; the whole Settings needs more."""
    others = tuple(name for name in REQUIRED if name != "database_url")
    _clear(monkeypatch, others)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")

    assert (
        DatabaseSettings(_env_file=None).database_url
        == "postgresql+asyncpg://u:p@localhost:5432/db"
    )
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)
    assert {e["loc"] for e in exc_info.value.errors()} == {(name,) for name in others}


@pytest.mark.parametrize("getter", [get_settings, get_database_settings])
def test_settings_getters_are_cached(getter: Callable[[], DatabaseSettings]) -> None:
    """Happy path: each getter builds its settings once and then returns the same instance."""
    assert getter() is getter()


def test_env_file_is_the_repository_root_dotenv() -> None:
    """Edge case: the .env path depends on the module location, not on the working directory."""
    assert Path(__file__).resolve().parents[1] / ".env" == ENV_FILE


def test_suite_settings_come_from_the_test_environment_not_from_dotenv() -> None:
    """Edge case: the root conftest.py fixes every setting, so no local .env value gets in."""
    assert get_settings() == Settings(_env_file=None)


def test_validation_errors_do_not_echo_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unhappy path: a startup failure names fields but never prints the values already read."""
    _clear(monkeypatch, ALL_FIELDS)
    monkeypatch.setenv("JWT_SECRET_KEY", "leak-sentinel-value")

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "leak-sentinel-value" not in str(exc_info.value)


def test_env_example_is_a_valid_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Happy path: .env.example, copied as is to .env, is a configuration the app loads."""
    _clear(monkeypatch, ALL_FIELDS)

    settings = Settings(_env_file=ENV_EXAMPLE)

    assert (
        settings.algorithm,
        settings.access_token_expire_minutes,
        settings.verification_token_expire_minutes,
    ) == ("HS256", 30, 15)


def test_env_example_documents_every_setting() -> None:
    """Edge case: every Settings field has its upper-case key in .env.example."""
    assert {n.upper() for n in Settings.model_fields} <= set(dotenv_values(ENV_EXAMPLE))


def test_test_environment_fixes_every_setting() -> None:
    """Edge case: the root conftest.py gives every Settings field a test value (ADR-0013, 6)."""
    test_environment = runpy.run_path(str(ROOT_CONFTEST))["TEST_ENVIRONMENT"]

    assert {n.upper() for n in Settings.model_fields} <= set(test_environment)


@pytest.mark.parametrize("field", tuple(BOOTSTRAP_VALUES))
def test_missing_bootstrap_variable_fails_naming_it(
    monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    """Unhappy path: the bootstrap command needs every credential; a missing one is named."""
    _set_bootstrap(monkeypatch)
    monkeypatch.delenv(field.upper())

    with pytest.raises(ValidationError) as exc_info:
        SuperadminBootstrapSettings(_env_file=None)

    assert [(e["type"], e["loc"]) for e in exc_info.value.errors()] == [("missing", (field,))]


def test_bootstrap_settings_need_no_web_app_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    """Happy path: the command runs without the JWT, mail and storage secrets of the web app."""
    _clear(monkeypatch, REQUIRED)
    _set_bootstrap(monkeypatch)

    settings = SuperadminBootstrapSettings(_env_file=None)

    assert set(SuperadminBootstrapSettings.model_fields) == set(BOOTSTRAP_VALUES)
    assert settings.superadmin_cedula == "900000001"
    assert settings.superadmin_password.get_secret_value() == "Bootstrap-sentinel-1"


def test_bootstrap_password_never_shows_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    """Edge case: printing or logging the settings object never reveals the password."""
    _set_bootstrap(monkeypatch)

    settings = SuperadminBootstrapSettings(_env_file=None)

    assert "Bootstrap-sentinel-1" not in repr(settings)
    assert "Bootstrap-sentinel-1" not in str(settings.model_dump())


def test_bootstrap_validation_errors_do_not_echo_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unhappy path: a missing credential fails without printing the password already read."""
    _set_bootstrap(monkeypatch)
    monkeypatch.delenv("SUPERADMIN_EMAIL")

    with pytest.raises(ValidationError) as exc_info:
        SuperadminBootstrapSettings(_env_file=None)

    assert "Bootstrap-sentinel-1" not in str(exc_info.value)


def test_env_example_documents_every_bootstrap_variable() -> None:
    """Edge case: every SuperadminBootstrapSettings field has its upper-case key in .env.example."""
    assert {n.upper() for n in SuperadminBootstrapSettings.model_fields} <= set(
        dotenv_values(ENV_EXAMPLE)
    )


def test_env_example_password_is_not_a_usable_credential(monkeypatch: pytest.MonkeyPatch) -> None:
    """Edge case: the example password, copied as is, fails the account rules (ADR-0015)."""
    _clear(monkeypatch, tuple(BOOTSTRAP_VALUES))
    settings = SuperadminBootstrapSettings(_env_file=ENV_EXAMPLE)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateByAdmin(
            cedula=settings.superadmin_cedula,
            email=settings.superadmin_email,
            first_name=settings.superadmin_first_name,
            last_name=settings.superadmin_last_name,
            password=settings.superadmin_password.get_secret_value(),
            data_consent=True,
            role=UserRole.superadmin,
            is_active=True,
        )

    assert [(e["type"], e["loc"]) for e in exc_info.value.errors()] == [
        ("value_error", ("password",))
    ]
