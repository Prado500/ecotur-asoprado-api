"""Tests for bootstrap_superadmin: the first superadmin of an empty platform (BE-34, ADR-0015).

Real repositories over the test database: what matters is which rows exist afterwards.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select

from app.core.exceptions import AlreadyExistsError
from app.core.security import verify_password
from app.models.audit import AuditAction, AuditLog
from app.models.user import User, UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateByAdmin
from app.schemas.user import UserRole as SchemaUserRole
from app.services.audit_service import AuditService
from app.services.superadmin_bootstrap import bootstrap_superadmin

PASSWORD = "Bootstrap2026x"


def _credentials(**overrides) -> UserCreateByAdmin:
    values = dict(
        cedula="900000001",
        email="root@test.com",
        first_name="Ana",
        last_name="Diaz",
        password=PASSWORD,
        data_consent=True,
        role=SchemaUserRole.superadmin,
        is_active=True,
    )
    values.update(overrides)
    return UserCreateByAdmin(**values)


async def _run(db_session, credentials: UserCreateByAdmin) -> User | None:
    return await bootstrap_superadmin(
        credentials,
        UserRepository(db_session),
        AuditService(AuditRepository(db_session)),
    )


async def _count(db_session, model: type[User] | type[AuditLog]) -> int:
    return int(await db_session.scalar(select(func.count()).select_from(model)))


async def test_bootstrap_creates_an_active_superadmin_on_an_empty_database(db_session):
    """Happy path: with no users, it creates the superadmin and audits it as its own author."""
    created = await _run(db_session, _credentials())

    assert created is not None
    user = await db_session.scalar(select(User))
    assert (user.cedula, user.email, user.first_name, user.last_name) == (
        "900000001",
        "root@test.com",
        "Ana",
        "Diaz",
    )
    assert (user.role, user.is_active, user.data_consent, user.deleted_at) == (
        UserRole.superadmin,
        True,
        True,
        None,
    )
    assert verify_password(PASSWORD, user.password_hash)
    log = await db_session.scalar(select(AuditLog))
    assert (log.entity_name, log.entity_id, log.action, log.performed_by, log.changes) == (
        "User",
        "900000001",
        AuditAction.CREATE,
        "900000001",
        {"role": "superadmin", "source": "bootstrap"},
    )


async def test_bootstrap_writes_nothing_when_an_active_superadmin_exists(db_session, persist_user):
    """Unhappy path: an active superadmin already exists, so nothing is created or audited."""
    await persist_user(role=UserRole.superadmin)

    assert await _run(db_session, _credentials()) is None

    assert await _count(db_session, User) == 1
    assert await _count(db_session, AuditLog) == 0


async def test_bootstrap_second_run_writes_nothing(db_session):
    """Edge case: idempotent; the second run finds the first superadmin and stops."""
    await _run(db_session, _credentials())

    assert await _run(db_session, _credentials(cedula="900000002", email="b@test.com")) is None

    assert await _count(db_session, User) == 1
    assert await _count(db_session, AuditLog) == 1


@pytest.mark.parametrize("shared", ["cedula", "email"])
@pytest.mark.parametrize(
    "existing",
    [
        {"role": UserRole.tourist, "is_active": True},
        {"role": UserRole.admin, "is_active": False},
        {
            "role": UserRole.superadmin,
            "is_active": False,
            "deleted_at": datetime(2026, 1, 1, tzinfo=UTC),
        },
    ],
    ids=["active-tourist", "inactive-admin", "deleted-superadmin"],
)
async def test_bootstrap_never_takes_over_an_existing_account(
    db_session, persist_user, shared, existing
):
    """Unhappy path: a cedula or email already in any row fails; nothing is promoted or written."""
    account = await persist_user(**existing)
    credentials = _credentials(**{shared: getattr(account, shared)})

    with pytest.raises(AlreadyExistsError):
        await _run(db_session, credentials)

    await db_session.refresh(account)
    assert (account.role, account.is_active, account.deleted_at is None) == (
        existing["role"],
        existing["is_active"],
        "deleted_at" not in existing,
    )
    assert await _count(db_session, User) == 1
    assert await _count(db_session, AuditLog) == 0


@pytest.mark.parametrize(
    "overrides",
    [{"is_active": False}, {"is_active": False, "deleted_at": datetime(2026, 1, 1, tzinfo=UTC)}],
    ids=["inactive", "soft-deleted"],
)
async def test_bootstrap_creates_when_no_superadmin_can_sign_in(
    db_session, persist_user, overrides
):
    """Edge case: superadmins that are inactive or deleted do not count; a new one is created."""
    await persist_user(role=UserRole.superadmin, **overrides)

    created = await _run(db_session, _credentials())

    assert created is not None
    assert (created.role, created.is_active) == (UserRole.superadmin, True)
    assert await _count(db_session, User) == 2


async def test_bootstrap_always_creates_an_active_superadmin(db_session):
    """Edge case: the role and is_active of the credentials are ignored, not trusted."""
    created = await _run(db_session, _credentials(role=SchemaUserRole.admin, is_active=False))

    assert created is not None
    await db_session.refresh(created)
    assert (created.role, created.is_active) == (UserRole.superadmin, True)
