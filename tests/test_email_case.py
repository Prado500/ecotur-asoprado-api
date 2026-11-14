"""Tests for BE-51: every email is stored in lowercase, so one email is one account (ADR-0016).

The schemas lower each email that comes in (LowercaseEmail), the CHECK ck_users_email_lowercase
refuses an uppercase letter written by any other path, and the unique index ix_users_email keeps
one account per email. One test per path that reads or writes an email (registration,
provisioning, bootstrap, login, email verification and the change by PATCH), and the migration
that adds the CHECK, run on a database of its own.
"""

import runpy
from collections.abc import Callable, Iterator
from pathlib import Path
from unittest.mock import ANY

import jwt
import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Connection, create_engine, func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AlreadyExistsError
from app.core.security import create_verification_token, get_password_hash
from app.db.database import Base
from app.models.audit import AuditLog
from app.models.user import User, UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserCreateByAdmin, UserLogin, UserUpdate
from app.schemas.user import UserRole as SchemaUserRole
from app.services.audit_service import AuditService
from app.services.superadmin_bootstrap import bootstrap_superadmin

PASSWORD = "Password123"
STORED = "root@test.com"
TYPED = "rOOT@Test.com"
CHECK_NAME = "ck_users_email_lowercase"

REGISTRATION = {
    "cedula": "1005911792",
    "email": TYPED,
    "first_name": "Juan",
    "last_name": "Perez",
    "password": PASSWORD,
    "data_consent": True,
}

MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "b51f3c9e2a64_users_email_stored_in_lowercase.py"
)


async def _emails(db_session) -> list[str]:
    return list(await db_session.scalars(select(User.email).order_by(User.id)))


def _migrate(connection: Connection, step: str) -> None:
    """Runs upgrade() or downgrade() of the BE-51 migration, with its own op, on this connection."""
    migration = runpy.run_path(str(MIGRATION))
    with Operations.context(MigrationContext.configure(connection)):
        migration[step]()


def _checks(connection: Connection) -> list[str | None]:
    return [check["name"] for check in inspect(connection).get_check_constraints("users")]


def _add(connection: Connection, user: User) -> None:
    with Session(connection) as session:
        session.add(user)
        session.commit()


@pytest.fixture
def pre_migration_db() -> Iterator[Connection]:
    """A SQLite database of its own, on the schema before b51f3c9e2a64 (its downgrade applied).

    The suite's shared database is left alone: on SQLite a failed batch leaves its temporary
    table behind, and the next test would find it.
    """
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        Base.metadata.create_all(connection)
        _migrate(connection, "downgrade")
        connection.commit()
        yield connection
    engine.dispose()


@pytest.mark.parametrize(
    "build",
    [
        lambda: UserCreate(**REGISTRATION),
        lambda: UserLogin(email=TYPED, password=PASSWORD),
        lambda: UserUpdate(email=TYPED),
    ],
    ids=["UserBase", "UserLogin", "UserUpdate"],
)
def test_every_email_input_arrives_lowercased(
    build: Callable[[], UserCreate | UserLogin | UserUpdate],
) -> None:
    """Happy path: the three schemas that take an email hand it over lowercased, local part too."""
    assert build().email == STORED


def test_a_non_ascii_local_part_is_lowercased_too() -> None:
    """Edge case: EmailStr admits a non-ASCII local part, and Python lowers it as Unicode."""
    assert UserLogin(email="ÁNGEL@Test.com", password=PASSWORD).email == "ángel@test.com"


def test_a_patch_with_a_null_email_keeps_it_null() -> None:
    """Edge case: the optional email of UserUpdate accepts None and does not lower it."""
    update = UserUpdate(email=None, phone="3001234567")

    assert update.email is None
    assert update.model_dump(exclude_unset=True) == {"email": None, "phone": "3001234567"}


async def test_registration_stores_the_email_in_lowercase(client, db_session, mock_send_email):
    """Happy path: 201; the row, the response and the verification email carry it lowercased."""
    response = await client.post("/usuarios/registro", json=REGISTRATION)

    assert response.status_code == 201
    assert response.json()["email"] == STORED
    assert await _emails(db_session) == [STORED]
    mock_send_email.assert_called_once_with(
        email_to=STORED, first_name="Juan", token=ANY, base_url=ANY
    )


async def test_registration_rejects_an_email_taken_in_another_case(
    client, db_session, persist_user, mock_send_email
):
    """Unhappy path: 400, no second row and no verification email."""
    await persist_user(email=STORED)

    response = await client.post("/usuarios/registro", json=REGISTRATION)

    assert response.status_code == 400
    assert set(response.json()) == {"detail"}
    assert await _emails(db_session) == [STORED]
    mock_send_email.assert_not_called()


async def test_provisioning_rejects_an_email_taken_in_another_case(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: a superadmin cannot provision a second account for the same email."""
    superadmin = await persist_user(role=UserRole.superadmin)
    await persist_user(email=STORED)
    payload = {**REGISTRATION, "cedula": "555555", "role": "admin", "is_active": True}

    response = await client.post(
        "/usuarios/admin", json=payload, headers=make_auth_headers(superadmin)
    )

    assert response.status_code == 400
    assert set(response.json()) == {"detail"}
    assert await _emails(db_session) == [superadmin.email, STORED]


async def test_bootstrap_rejects_an_email_taken_in_another_case(db_session, persist_user):
    """Unhappy path: SUPERADMIN_EMAIL in another case stops the bootstrap; nothing is written."""
    await persist_user(email=STORED)
    credentials = UserCreateByAdmin(
        **{**REGISTRATION, "cedula": "900000001"}, role=SchemaUserRole.superadmin, is_active=True
    )

    with pytest.raises(AlreadyExistsError):
        await bootstrap_superadmin(
            credentials, UserRepository(db_session), AuditService(AuditRepository(db_session))
        )

    assert await _emails(db_session) == [STORED]
    assert await db_session.scalar(select(func.count()).select_from(AuditLog)) == 0


async def test_login_accepts_the_email_typed_in_another_case(client, persist_user):
    """Happy path: 200, and the token carries the stored, lowercase email."""
    user = await persist_user(email=STORED, password_hash=get_password_hash(PASSWORD))

    response = await client.post("/usuarios/login", json={"email": TYPED, "password": PASSWORD})

    assert response.status_code == 200
    settings = get_settings()
    claims = jwt.decode(
        response.json()["access_token"], settings.jwt_secret_key, algorithms=[settings.algorithm]
    )
    assert claims["sub"] == user.email == STORED


async def test_verification_token_in_another_case_is_rejected(client, db_session, persist_user):
    """Edge case: the app signs only the stored email, so a subject in another case finds none."""
    user = await persist_user(email=STORED, is_active=False)
    token = create_verification_token(TYPED)

    response = await client.get(f"/usuarios/verificar-email?token={token}")

    assert response.status_code == 404
    assert set(response.json()) == {"detail"}
    await db_session.refresh(user)
    assert user.is_active is False


async def test_patch_stores_a_new_email_in_lowercase(
    client, db_session, persist_user, make_auth_headers
):
    """Happy path: 200; the response and the row carry the new email lowercased."""
    user = await persist_user()

    response = await client.patch(
        f"/usuarios/{user.cedula}", json={"email": TYPED}, headers=make_auth_headers(user)
    )

    assert response.status_code == 200
    assert response.json()["email"] == STORED
    await db_session.refresh(user)
    assert user.email == STORED


async def test_patch_cannot_take_an_email_in_another_case(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: 409 from the unique index ix_users_email; the target keeps its email."""
    admin = await persist_user(role=UserRole.admin)
    await persist_user(email=STORED)
    tourist = await persist_user()
    original_email = tourist.email

    response = await client.patch(
        f"/usuarios/{tourist.cedula}", json={"email": TYPED}, headers=make_auth_headers(admin)
    )

    assert response.status_code == 409
    assert set(response.json()) == {"detail"}
    await db_session.refresh(tourist)
    assert tourist.email == original_email


async def test_patch_changing_only_the_case_keeps_the_email(
    client, db_session, persist_user, make_auth_headers
):
    """Edge case: its own email in another case is the same value once lowercased."""
    user = await persist_user(email=STORED)

    response = await client.patch(
        f"/usuarios/{user.cedula}", json={"email": TYPED}, headers=make_auth_headers(user)
    )

    assert response.status_code == 200
    assert response.json()["email"] == STORED
    await db_session.refresh(user)
    assert user.email == STORED


async def test_database_rejects_an_email_with_an_uppercase_letter(db_session, make_user):
    """Unhappy path: a row written without a schema still meets the CHECK (ADR-0002)."""
    db_session.add(make_user(email="Root@test.com"))

    with pytest.raises(IntegrityError, match=CHECK_NAME):
        await db_session.commit()

    await db_session.rollback()
    assert await _emails(db_session) == []


def test_migration_adds_the_check_and_its_downgrade_drops_it(pre_migration_db, make_user):
    """Happy path: upgrade keeps rows and unique indexes and adds the CHECK; downgrade drops it."""
    _add(pre_migration_db, make_user(email=STORED))
    assert _checks(pre_migration_db) == []

    _migrate(pre_migration_db, "upgrade")

    assert _checks(pre_migration_db) == [CHECK_NAME]
    assert list(pre_migration_db.scalars(select(User.email))) == [STORED]
    indexes = inspect(pre_migration_db).get_indexes("users")
    assert {index["name"] for index in indexes if index["unique"]} == {
        "ix_users_cedula",
        "ix_users_email",
    }
    _migrate(pre_migration_db, "downgrade")
    assert _checks(pre_migration_db) == []


def test_migration_stops_on_an_email_with_an_uppercase_letter(pre_migration_db, make_user):
    """Unhappy path: one uppercase row stops the upgrade; row and table stay as they were."""
    _add(pre_migration_db, make_user(email="Juan@test.com"))

    with pytest.raises(IntegrityError, match=CHECK_NAME):
        _migrate(pre_migration_db, "upgrade")

    pre_migration_db.rollback()
    assert _checks(pre_migration_db) == []
    assert list(pre_migration_db.scalars(select(User.email))) == ["Juan@test.com"]
