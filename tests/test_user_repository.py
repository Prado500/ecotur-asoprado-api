"""Tests for the UserRepository queries that decide who counts: which superadmins can sign in
and which account may receive a new verification link (ADR-0023)."""

from datetime import UTC, datetime, timedelta

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


# The cutoff a resend passes: now minus the interval, fixed here so the boundary is exact.
SENT_BEFORE = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    "overrides",
    [
        {"is_active": False},
        {"is_active": True},
        {"is_active": False, "verification_sent_at": SENT_BEFORE - timedelta(minutes=5)},
        {"is_active": False, "verification_sent_at": SENT_BEFORE},
    ],
    ids=[
        "inactive-never-sent",
        "active-unverified",
        "sent-before-the-cutoff",
        "sent-at-the-cutoff",
    ],
)
async def test_tourist_due_a_verification_link_is_found(db_session, persist_user, overrides):
    """Happy path: a non-deleted, unverified tourist, active or not, past the interval."""
    tourist = await persist_user(role=UserRole.tourist, **overrides)

    found = await UserRepository(db_session).get_tourist_due_a_verification_link(
        tourist.email, sent_before=SENT_BEFORE
    )

    assert found is tourist


@pytest.mark.parametrize(
    "overrides",
    [
        {"role": UserRole.admin, "is_active": False},
        {"role": UserRole.superadmin, "is_active": False},
        {"is_active": False, "deleted_at": SENT_BEFORE},
        {"is_active": False, "email_verified_at": SENT_BEFORE},
        {"is_active": False, "verification_sent_at": SENT_BEFORE + timedelta(microseconds=1)},
    ],
    ids=["admin", "superadmin", "soft-deleted", "verified", "sent-after-the-cutoff"],
)
async def test_account_not_due_a_verification_link_is_not_found(
    db_session, persist_user, overrides
):
    """Unhappy path: administrative, deleted or verified accounts, or a link still too recent."""
    account = await persist_user(**overrides)

    found = await UserRepository(db_session).get_tourist_due_a_verification_link(
        account.email, sent_before=SENT_BEFORE
    )

    assert found is None


async def test_due_verification_link_lookup_matches_only_its_email(db_session, persist_user):
    """Edge case: a tourist due a link is not returned for another address."""
    await persist_user(role=UserRole.tourist, is_active=False)

    found = await UserRepository(db_session).get_tourist_due_a_verification_link(
        "otra@test.com", sent_before=SENT_BEFORE
    )

    assert found is None
