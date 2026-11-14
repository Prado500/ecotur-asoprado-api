"""Tests for the bootstrap command, python -m app.cli.bootstrap_superadmin (BE-34, ADR-0015).

The command opens its own engine from DATABASE_URL, so each test points it at a file database
of its own, with the schema already created. Every variable is set in the process environment,
which beats any developer .env file (ADR-0013, point 3).
"""

import asyncio
import os
import runpy
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.cli.bootstrap_superadmin import main
from app.core.security import verify_password
from app.db.database import Base
from app.models.audit import AuditLog
from app.models.user import User, UserRole

PASSWORD = "Bootstrap-sentinel-7"

VALID_VARIABLES = {
    "SUPERADMIN_CEDULA": "900000001",
    "SUPERADMIN_EMAIL": "root@test.com",
    "SUPERADMIN_FIRST_NAME": "Ana",
    "SUPERADMIN_LAST_NAME": "Diaz",
    "SUPERADMIN_PASSWORD": PASSWORD,
}

# The required secrets of Settings: the web app needs them, the command must not (ADR-0015).
WEB_APP_SECRETS = (
    "JWT_SECRET_KEY",
    "MAIL_USERNAME",
    "MAIL_PASSWORD",
    "AZURE_STORAGE_CONNECTION_STRING",
)

REPO_ROOT = Path(__file__).resolve().parents[1]


async def _create_schema(url: str) -> None:
    """Creates every table in the database at url."""
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def _execute(url: str, statement: Any) -> list[Any]:
    """Runs one statement on an engine of its own, commits, and returns its rows, if any."""
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        result = await conn.execute(statement)
        rows = list(result.all()) if result.returns_rows else []
    await engine.dispose()
    return rows


async def _add(url: str, user: User) -> None:
    """Commits user to the database at url, in a session over an engine of its own.

    Not persist_user: it writes to the suite's in-memory database, and the command reads the
    file database at url.
    """
    engine = create_async_engine(url)
    async with AsyncSession(engine) as session:
        session.add(user)
        await session.commit()
    await engine.dispose()


def _count(url: str, model: type[User] | type[AuditLog]) -> int:
    return int(asyncio.run(_execute(url, select(func.count()).select_from(model)))[0][0])


@pytest.fixture
def database_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """A file database with the schema created, and the command's six variables set."""
    url = f"sqlite+aiosqlite:///{tmp_path / 'bootstrap.db'}"
    asyncio.run(_create_schema(url))
    monkeypatch.setenv("DATABASE_URL", url)
    for name, value in VALID_VARIABLES.items():
        monkeypatch.setenv(name, value)
    return url


def test_command_creates_the_superadmin_without_writing_secrets(
    database_url: str, capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture
) -> None:
    """Happy path: exit 0, one active superadmin, one audit entry; no password or hash shown."""
    assert main() == 0

    users = asyncio.run(
        _execute(database_url, select(User.cedula, User.role, User.is_active, User.password_hash))
    )
    assert [(u.cedula, u.role, u.is_active) for u in users] == [
        ("900000001", UserRole.superadmin, True)
    ]
    assert verify_password(PASSWORD, users[0].password_hash)
    assert _count(database_url, AuditLog) == 1
    output = capsys.readouterr()
    assert output.err == ""
    assert PASSWORD not in output.out
    assert users[0].password_hash not in output.out + caplog.text


def test_command_second_run_exits_zero_and_writes_nothing(
    database_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Edge case: an operator may run it twice; the second run changes nothing."""
    assert main() == 0

    assert main() == 0

    assert (_count(database_url, User), _count(database_url, AuditLog)) == (1, 1)
    output = capsys.readouterr()
    assert output.err == ""
    assert PASSWORD not in output.out


def test_command_fails_when_the_email_belongs_to_another_account(
    database_url: str, make_user: Callable[..., User], capsys: pytest.CaptureFixture[str]
) -> None:
    """Unhappy path: exit 1 with nothing written; the tourist keeps its role."""
    asyncio.run(_add(database_url, make_user(cedula="2000000002", email="root@test.com")))

    assert main() == 1

    users = asyncio.run(_execute(database_url, select(User.cedula, User.role)))
    assert [(u.cedula, u.role) for u in users] == [("2000000002", UserRole.tourist)]
    assert _count(database_url, AuditLog) == 0
    output = capsys.readouterr()
    assert output.out == ""
    assert PASSWORD not in output.err


@pytest.mark.parametrize(
    ("variable", "value", "expected_err"),
    [
        ("SUPERADMIN_PASSWORD", "sinmayuscula1", "SUPERADMIN_PASSWORD: value_error\n"),
        ("SUPERADMIN_CEDULA", "12AB", "SUPERADMIN_CEDULA: string_too_short\n"),
        ("DATABASE_URL", "", "DATABASE_URL: string_too_short\n"),
    ],
    ids=["weak-password", "short-cedula", "empty-database-url"],
)
def test_command_rejects_bad_configuration_naming_only_the_variable(
    database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    variable: str,
    value: str,
    expected_err: str,
) -> None:
    """Unhappy path: exit 1 before any write; stderr names the variable, never a value."""
    monkeypatch.setenv(variable, value)

    assert main() == 1

    assert _count(database_url, User) == 0
    assert capsys.readouterr() == ("", expected_err)


def test_command_runs_as_a_module_and_exits_with_the_code_of_main(
    database_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Edge case: python -m app.cli.bootstrap_superadmin exits with what main returns."""
    monkeypatch.setenv("SUPERADMIN_PASSWORD", "sinmayuscula1")
    monkeypatch.delitem(sys.modules, "app.cli.bootstrap_superadmin")

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("app.cli.bootstrap_superadmin", run_name="__main__")

    assert exc_info.value.code == 1
    assert _count(database_url, User) == 0


def test_command_runs_without_the_web_app_secrets(database_url: str) -> None:
    """Edge case: run as a child process with the web app secrets empty, it still creates it.

    The suite's environment carries every secret (root conftest.py), so a test that calls main()
    cannot see an import that builds Settings. Empty values beat any .env file (ADR-0013, point
    3) and fail Field(min_length=1): if the command built Settings, the child would exit 1.
    """
    env = os.environ | dict.fromkeys(WEB_APP_SECRETS, "")

    completed = subprocess.run(
        [sys.executable, "-m", "app.cli.bootstrap_superadmin"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    users = asyncio.run(_execute(database_url, select(User.cedula, User.role, User.is_active)))
    assert [(u.cedula, u.role, u.is_active) for u in users] == [
        ("900000001", UserRole.superadmin, True)
    ]
    assert PASSWORD not in completed.stdout + completed.stderr
