"""Tests for UserRepository.count_active_superadmins: which superadmins can sign in."""

from datetime import UTC, datetime

import pytest

from app.models.user import UserRole
from app.repositories.user_repository import UserRepository


async def test_count_active_superadmins_counts_each_active_one(db_session, persist_user):
    """Happy path: every active, non-deleted superadmin is counted, and only those."""
    await persist_user(role=UserRole.superadmin)
    await persist_user(role=UserRole.superadmin)
    await persist_user(role=UserRole.admin)
    await persist_user(role=UserRole.tourist)

    assert await UserRepository(db_session).count_active_superadmins() == 2


async def test_count_active_superadmins_on_empty_database_is_zero(db_session):
    """Edge case: with no users at all, the count is zero, not None."""
    assert await UserRepository(db_session).count_active_superadmins() == 0


@pytest.mark.parametrize(
    "overrides",
    [
        {"is_active": False},
        {"is_active": False, "deleted_at": datetime(2026, 1, 1, tzinfo=UTC)},
        {"is_active": True, "deleted_at": datetime(2026, 1, 1, tzinfo=UTC)},
    ],
    ids=["inactive", "soft-deleted", "deleted-but-active-flag"],
)
async def test_count_active_superadmins_skips_those_who_cannot_sign_in(
    db_session, persist_user, overrides
):
    """Unhappy path: an inactive or soft-deleted superadmin does not count."""
    await persist_user(role=UserRole.superadmin, **overrides)

    assert await UserRepository(db_session).count_active_superadmins() == 0
