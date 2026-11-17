"""Test suite for the extracted UserAccessPolicy authorization rules.

Freezes the pure hierarchical ABAC invariants at the domain-policy level
(unit tests), the transport-domain contract through the real HTTP stack
(integration tests), and the AuthorizationError -> HTTP 403 mapping
(global-handler tests).
"""

import json
from datetime import UTC, datetime
from unittest.mock import create_autospec

import pytest
from sqlalchemy import select
from starlette.requests import Request

from app.api.dependencies import get_user_service
from app.core.exceptions import AuthorizationError
from app.core.security import get_password_hash
from app.main import app, domain_error_handler
from app.models.audit import AuditAction, AuditLog
from app.models.user import User, UserRole
from app.services.user_access_policy import UserAccessPolicy
from app.services.user_service import UserService


@pytest.fixture
def policy() -> UserAccessPolicy:
    """Provides a fresh UserAccessPolicy instance for pure unit tests."""
    return UserAccessPolicy()


# ==========================================
# A. PURE UNIT TESTS (no DB, no HTTP stack)
# ==========================================


class TestAssertCanDelete:
    """Freezes the deletion invariant: higher rank, or own account only for a tourist."""

    def test_self_delete_tourist_is_allowed(self, policy, make_user):
        tourist = make_user(role=UserRole.tourist)

        policy.assert_can_delete(tourist, tourist)

    def test_admin_can_delete_tourist(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.tourist)

        policy.assert_can_delete(actor, target)

    def test_superadmin_can_delete_admin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.admin)

        policy.assert_can_delete(actor, target)

    def test_be35_superadmin_self_delete_is_rejected(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_delete(superadmin, superadmin)

    def test_be35_self_delete_guard_identifies_the_actor_by_cedula(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)
        twin = make_user(role=UserRole.superadmin, cedula=superadmin.cedula)

        with pytest.raises(AuthorizationError):
            policy.assert_can_delete(superadmin, twin)

    def test_be58_admin_self_delete_is_rejected(self, policy, make_user):
        admin = make_user(role=UserRole.admin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_delete(admin, admin)

    def test_tourist_cannot_delete_other_tourist(self, policy, make_user):
        actor = make_user(role=UserRole.tourist)
        target = make_user(role=UserRole.tourist)

        with pytest.raises(AuthorizationError):
            policy.assert_can_delete(actor, target)

    def test_tourist_cannot_delete_admin(self, policy, make_user):
        actor = make_user(role=UserRole.tourist)
        target = make_user(role=UserRole.admin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_delete(actor, target)

    def test_admin_cannot_delete_peer_admin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.admin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_delete(actor, target)

    def test_superadmin_cannot_delete_peer_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_delete(actor, target)


class TestAssertCanUpdate:
    """Freezes update invariants: hierarchy, role and is_active fail-safes, ADR-0017 guard."""

    def test_tourist_self_update_basic_fields_is_allowed(self, policy, make_user):
        tourist = make_user(role=UserRole.tourist)

        policy.assert_can_update(tourist, tourist, {"first_name": "Updated"})

    def test_admin_can_update_tourist(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.tourist)

        policy.assert_can_update(actor, target, {"email": "new@test.com"})

    def test_superadmin_can_mutate_role(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.tourist)

        policy.assert_can_update(actor, target, {"role": UserRole.admin})

    def test_admin_can_mutate_is_active(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.tourist)

        policy.assert_can_update(actor, target, {"is_active": False})

    def test_admin_cannot_update_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"first_name": "Hacked"})

    def test_tourist_role_escalation_rejected(self, policy, make_user):
        tourist = make_user(role=UserRole.tourist)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(tourist, tourist, {"role": UserRole.admin})

    def test_admin_role_escalation_rejected(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.tourist)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"role": UserRole.superadmin})

    def test_tourist_cannot_mutate_is_active(self, policy, make_user):
        tourist = make_user(role=UserRole.tourist)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(tourist, tourist, {"is_active": True})

    def test_tourist_cannot_self_escalate_own_role(self, policy, make_user):
        tourist = make_user(role=UserRole.tourist)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(tourist, tourist, {"role": UserRole.superadmin})

    def test_superadmin_cannot_update_peer_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"first_name": "Hacked"})

    def test_tourist_cannot_update_other_tourist(self, policy, make_user):
        actor = make_user(role=UserRole.tourist)
        target = make_user(role=UserRole.tourist)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"last_name": "Changed"})

    @pytest.mark.parametrize("actor_role", list(UserRole))
    @pytest.mark.parametrize("new_role", list(UserRole))
    def test_be02_nobody_can_send_own_role(self, policy, make_user, actor_role, new_role):
        actor = make_user(role=actor_role)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, actor, {"role": new_role.value})

    def test_be02_superadmin_self_update_with_role_none_is_rejected(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(superadmin, superadmin, {"role": None})

    def test_be02_self_role_guard_identifies_the_actor_by_cedula(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)
        twin = make_user(role=UserRole.superadmin, cedula=superadmin.cedula)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(superadmin, twin, {"role": "tourist"})

    def test_be02_twin_by_cedula_with_profile_fields_is_self_update(self, policy, make_user):
        """Freezes that "self" means same cedula, not same instance or same email.

        A distinct instance with the actor's cedula must still be treated as a
        self-update: profile fields pass. If identity were compared by object or
        by email, the hierarchy guard (superadmin vs superadmin) would raise.
        """
        superadmin = make_user(role=UserRole.superadmin)
        twin = make_user(role=UserRole.superadmin, cedula=superadmin.cedula)

        policy.assert_can_update(superadmin, twin, {"first_name": "Updated"})

    def test_be02_superadmin_self_update_profile_fields_is_allowed(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)

        policy.assert_can_update(superadmin, superadmin, {"first_name": "Updated"})

    def test_role_guard_for_non_superadmins_runs_before_the_self_role_guard(
        self, policy, make_user
    ):
        """Freezes the guard order without reading the text.

        An admin sending its own role gets the non-superadmin answer, the same one it gets
        for someone else's role, and not the self-update answer a superadmin gets.
        """
        admin = make_user(role=UserRole.admin)
        tourist = make_user(role=UserRole.tourist)
        superadmin = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError) as admin_self:
            policy.assert_can_update(admin, admin, {"role": "admin"})
        with pytest.raises(AuthorizationError) as admin_other:
            policy.assert_can_update(admin, tourist, {"role": "admin"})
        with pytest.raises(AuthorizationError) as superadmin_self:
            policy.assert_can_update(superadmin, superadmin, {"role": "superadmin"})

        assert admin_self.value.detail == admin_other.value.detail
        assert admin_self.value.detail != superadmin_self.value.detail

    def test_be35_superadmin_self_deactivation_is_rejected(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(superadmin, superadmin, {"is_active": False})

    def test_be35_superadmin_self_update_with_is_active_true_is_allowed(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)

        policy.assert_can_update(superadmin, superadmin, {"is_active": True})

    def test_be35_self_deactivation_guard_identifies_the_actor_by_cedula(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)
        twin = make_user(role=UserRole.superadmin, cedula=superadmin.cedula)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(superadmin, twin, {"is_active": False})

    def test_be58_admin_self_deactivation_is_rejected(self, policy, make_user):
        admin = make_user(role=UserRole.admin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(admin, admin, {"is_active": False})

    def test_be35_superadmin_can_deactivate_lower_rank_account(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)
        admin = make_user(role=UserRole.admin)

        policy.assert_can_update(superadmin, admin, {"is_active": False})

    def test_be36_superadmin_can_reactivate_peer_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin, is_active=False)

        policy.assert_can_update(actor, target, {"is_active": True})

    def test_be36_peer_superadmin_deactivation_is_rejected(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"is_active": False})

    @pytest.mark.parametrize(
        "update_dict",
        [
            {"is_active": True, "first_name": "Changed"},
            {"is_active": True, "role": "superadmin"},
            {"role": "admin"},
            {"is_active": None},
            {},
        ],
        ids=["with-profile-field", "with-role", "role-only", "null", "empty"],
    )
    def test_be36_peer_superadmin_update_other_than_reactivation_is_rejected(
        self, policy, make_user, update_dict
    ):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin, is_active=False)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, update_dict)

    def test_be36_superadmin_cannot_reactivate_peer_in_recycle_bin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin, is_active=False, deleted_at=datetime.now(UTC))

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"is_active": True})

    def test_be36_admin_cannot_reactivate_peer_admin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.admin, is_active=False)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"is_active": True})

    def test_be36_admin_cannot_reactivate_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.superadmin, is_active=False)

        with pytest.raises(AuthorizationError):
            policy.assert_can_update(actor, target, {"is_active": True})


class TestAssertCanRecover:
    """Freezes recovery precedence: admins cannot restore equal/higher tiers."""

    def test_admin_can_recover_tourist(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.tourist)

        policy.assert_can_recover(actor, target)

    def test_superadmin_can_recover_admin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.admin)

        policy.assert_can_recover(actor, target)

    def test_superadmin_can_recover_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)
        target = make_user(role=UserRole.superadmin)

        policy.assert_can_recover(actor, target)

    def test_admin_cannot_recover_peer_admin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.admin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_recover(actor, target)

    def test_admin_cannot_recover_superadmin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)
        target = make_user(role=UserRole.superadmin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_recover(actor, target)


class TestCanSee:
    """Freezes the visibility denylist: only (admin, superadmin) is obscured."""

    def test_admin_cannot_see_superadmin(self, policy):
        assert policy.can_see(UserRole.admin, UserRole.superadmin) is False

    def test_admin_can_see_tourist(self, policy):
        assert policy.can_see(UserRole.admin, UserRole.tourist) is True

    def test_superadmin_can_see_superadmin(self, policy):
        assert policy.can_see(UserRole.superadmin, UserRole.superadmin) is True

    def test_tourist_can_see_superadmin(self, policy):
        assert policy.can_see(UserRole.tourist, UserRole.superadmin) is True


# ==========================================
# B. INTEGRATION TESTS (real HTTP stack, real tokens)
# ==========================================


async def test_delete_hierarchy_violation_returns_403_detail(
    client, db_session, persist_user, make_auth_headers
):
    """Admin deleting a superadmin yields 403 with the detail key; target stays active."""
    admin = await persist_user(role=UserRole.admin)
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.delete(
        f"/usuarios/{superadmin.cedula}",
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert "detail" in response.json()

    await db_session.refresh(superadmin)
    assert superadmin.deleted_at is None


async def test_patch_nonexistent_cedula_returns_404_before_403(
    client, persist_user, make_auth_headers
):
    """Order invariant: 404 (existence) precedes 403 (permissions) on PATCH."""
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        "/usuarios/9999999999",
        json={"first_name": "Ghost"},
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_delete_nonexistent_cedula_returns_404_before_403(
    client, persist_user, make_auth_headers
):
    """Order invariant: 404 (existence) precedes 403 (permissions) on DELETE."""
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.delete(
        "/usuarios/9999999999",
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_admin_cannot_escalate_tourist_to_superadmin_via_patch(
    client, db_session, persist_user, make_auth_headers
):
    """Admin promoting a tourist to superadmin yields 403 with no mutation."""
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"role": "superadmin"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert "detail" in response.json()

    await db_session.refresh(tourist)
    assert tourist.role == UserRole.tourist


async def test_admin_cannot_escalate_tourist_to_admin_via_patch(
    client, db_session, persist_user, make_auth_headers
):
    """Two-step proxy escalation: admin promoting a tourist to admin yields 403 with no mutation."""
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"role": "admin"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert "detail" in response.json()

    await db_session.refresh(tourist)
    assert tourist.role == UserRole.tourist


# --- B2 regression: an admin must not change their own role (audit B2) ---


async def test_b2_admin_self_promotion_to_superadmin_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """An admin PATCHing their own cedula to superadmin gets 403; nothing is written."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": "superadmin"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(admin)
    assert admin.role == UserRole.admin
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_b2_admin_self_demotion_to_tourist_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """An admin PATCHing their own role down to tourist gets 403; the role is kept."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": "tourist"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(admin)
    assert admin.role == UserRole.admin


async def test_b2_admin_self_update_without_role_returns_200(
    client, db_session, persist_user, make_auth_headers
):
    """An admin PATCHing their own profile without a role key succeeds and persists it."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"first_name": "Changed"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Changed"
    assert body["cedula"] == admin.cedula

    await db_session.refresh(admin)
    assert admin.first_name == "Changed"
    assert admin.role == UserRole.admin


async def test_b2_admin_self_role_noop_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """The role key itself is blocked: resending the admin's current role still gets 403."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": "admin"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(admin)
    assert admin.role == UserRole.admin


async def test_b2_admin_self_promotion_with_profile_fields_mutates_nothing(
    client, db_session, persist_user, make_auth_headers
):
    """A role key mixed with profile fields rejects the whole PATCH: no field changes."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": "superadmin", "first_name": "Changed"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(admin)
    assert admin.first_name == "John"
    assert admin.role == UserRole.admin


# --- BE-02 regression: nobody changes their own role, superadmin included ---


@pytest.mark.parametrize("new_role", ["tourist", "admin"])
async def test_be02_superadmin_self_role_change_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers, new_role
):
    """A superadmin PATCHing their own role down gets 403; nothing is written."""
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"role": new_role},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(superadmin)
    assert superadmin.role == UserRole.superadmin
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be02_superadmin_self_role_noop_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """The role key itself is blocked: resending the superadmin's current role still gets 403."""
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"role": "superadmin"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(superadmin)
    assert superadmin.role == UserRole.superadmin
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be02_superadmin_self_role_with_profile_fields_mutates_nothing(
    client, db_session, persist_user, make_auth_headers
):
    """A role key mixed with profile fields rejects the whole PATCH: no field changes."""
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"role": "tourist", "first_name": "Changed"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(superadmin)
    assert superadmin.first_name == "John"
    assert superadmin.role == UserRole.superadmin


async def test_be02_superadmin_keeps_powers_after_rejected_self_demotion(
    client, db_session, persist_user, make_auth_headers
):
    """After a rejected self-demotion the same token still changes third-party roles."""
    superadmin = await persist_user(role=UserRole.superadmin)
    tourist = await persist_user(role=UserRole.tourist)
    headers = make_auth_headers(superadmin)

    rejected = await client.patch(
        f"/usuarios/{superadmin.cedula}", json={"role": "tourist"}, headers=headers
    )
    accepted = await client.patch(
        f"/usuarios/{tourist.cedula}", json={"role": "admin"}, headers=headers
    )

    assert rejected.status_code == 403
    assert accepted.status_code == 200
    assert accepted.json()["role"] == "admin"

    await db_session.refresh(tourist)
    assert tourist.role == UserRole.admin


async def test_be02_superadmin_self_profile_update_returns_200(
    client, db_session, persist_user, make_auth_headers
):
    """A superadmin still edits their own profile; the audit row records exactly that change."""
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"first_name": "Changed"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["first_name"] == "Changed"
    assert body["cedula"] == superadmin.cedula

    await db_session.refresh(superadmin)
    assert superadmin.first_name == "Changed"
    assert superadmin.role == UserRole.superadmin

    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert len(audits) == 1
    assert audits[0].action == AuditAction.UPDATE
    assert audits[0].performed_by == superadmin.cedula
    assert audits[0].changes == {"first_name": "Changed"}


async def test_be02_superadmin_changes_third_party_role_returns_200(
    client, db_session, persist_user, make_auth_headers
):
    """A superadmin still changes a lower-rank account's role; the audit row names both ends."""
    superadmin = await persist_user(role=UserRole.superadmin)
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": "tourist"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "tourist"
    assert body["cedula"] == admin.cedula

    await db_session.refresh(admin)
    assert admin.role == UserRole.tourist

    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert len(audits) == 1
    assert audits[0].entity_id == admin.cedula
    assert audits[0].performed_by == superadmin.cedula
    assert audits[0].changes == {"role": "tourist"}


# --- B3 regression: a superadmin deletes third-party accounts (audit B3) ---


@pytest.mark.parametrize(
    "target_role", [UserRole.admin, UserRole.tourist], ids=["admin", "tourist"]
)
async def test_b3_superadmin_deletes_third_party_account(
    client, db_session, persist_user, make_auth_headers, target_role
):
    """A superadmin soft-deletes a lower-rank account and the audit row names the actor."""
    superadmin = await persist_user(role=UserRole.superadmin)
    target = await persist_user(role=target_role)

    response = await client.delete(
        f"/usuarios/{target.cedula}",
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"success", "message"}
    assert body["success"] is True
    assert isinstance(body["message"], str)

    await db_session.refresh(target)
    assert target.deleted_at is not None
    assert target.is_active is False

    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert len(audits) == 1
    assert audits[0].entity_id == target.cedula
    assert audits[0].action == AuditAction.SOFT_DELETE
    assert audits[0].performed_by == superadmin.cedula


async def test_b3_superadmin_deleting_peer_superadmin_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """A superadmin cannot delete another superadmin: 403 and the target stays alive."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin)

    response = await client.delete(
        f"/usuarios/{peer.cedula}",
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(peer)
    assert peer.deleted_at is None
    assert peer.is_active is True


async def test_b3_admin_deleting_peer_admin_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """An admin cannot delete another admin: 403 and the target stays alive."""
    admin = await persist_user(role=UserRole.admin)
    peer = await persist_user(role=UserRole.admin)

    response = await client.delete(
        f"/usuarios/{peer.cedula}",
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(peer)
    assert peer.deleted_at is None
    assert peer.is_active is True


async def test_b3_superadmin_deleting_already_deleted_account_returns_404(
    client, db_session, persist_user, make_auth_headers
):
    """Deleting an account already in the recycle bin is a 404 and writes no audit row."""
    superadmin = await persist_user(role=UserRole.superadmin)
    target = await persist_user(
        role=UserRole.tourist, deleted_at=datetime.now(UTC), is_active=False
    )

    response = await client.delete(
        f"/usuarios/{target.cedula}",
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 404
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_b3_superadmin_deleting_missing_cedula_returns_404(
    client, persist_user, make_auth_headers
):
    """Deleting a cedula that matches no account is a 404 with the detail shape."""
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.delete(
        "/usuarios/9999999999",
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 404
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)


# --- BE-35 regression: a superadmin never deletes or deactivates their own account ---


async def test_be35_sole_superadmin_self_delete_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """The only superadmin DELETEing their own account gets 403; nothing is written."""
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.delete(
        f"/usuarios/{superadmin.cedula}",
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(superadmin)
    assert superadmin.deleted_at is None
    assert superadmin.is_active is True
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active(
    client, db_session, persist_user, make_auth_headers
):
    """The rule does not count: with a second superadmin active, self-deletion is still 403."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin)

    response = await client.delete(
        f"/usuarios/{superadmin.cedula}",
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(superadmin)
    await db_session.refresh(peer)
    assert superadmin.deleted_at is None
    assert superadmin.is_active is True
    assert peer.is_active is True


@pytest.mark.parametrize(
    "payload",
    [{"is_active": False}, {"is_active": "false"}, {"is_active": False, "first_name": "Changed"}],
    ids=["false", "coerced-false", "with-profile-fields"],
)
async def test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers, payload
):
    """The only superadmin PATCHing their own is_active to false gets 403; nothing is written."""
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json=payload,
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(superadmin)
    assert superadmin.is_active is True
    assert superadmin.first_name == "John"
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active(
    client, db_session, persist_user, make_auth_headers
):
    """The rule does not count: with a second superadmin active, self-deactivation is still 403."""
    superadmin = await persist_user(role=UserRole.superadmin)
    await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"is_active": False},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(superadmin)
    assert superadmin.is_active is True


async def test_be35_superadmin_keeps_access_after_rejected_self_removal(
    client, db_session, persist_user, make_auth_headers
):
    """After both self-removals are rejected, the same token still reads its own profile."""
    superadmin = await persist_user(role=UserRole.superadmin)
    headers = make_auth_headers(superadmin)

    deleted = await client.delete(f"/usuarios/{superadmin.cedula}", headers=headers)
    deactivated = await client.patch(
        f"/usuarios/{superadmin.cedula}", json={"is_active": False}, headers=headers
    )
    profile = await client.get("/usuarios/mi-perfil", headers=headers)

    assert deleted.status_code == 403
    assert deactivated.status_code == 403
    assert profile.status_code == 200
    body = profile.json()
    assert body["cedula"] == superadmin.cedula
    assert body["role"] == "superadmin"
    assert body["is_active"] is True

    await db_session.refresh(superadmin)
    assert superadmin.deleted_at is None
    assert superadmin.is_active is True


async def test_be35_superadmin_self_update_with_is_active_true_returns_200(
    client, db_session, persist_user, make_auth_headers
):
    """The guard reads the value: is_active true on one's own account still succeeds."""
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"is_active": True},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cedula"] == superadmin.cedula
    assert body["is_active"] is True

    await db_session.refresh(superadmin)
    assert superadmin.is_active is True


async def test_be35_superadmin_deactivates_lower_rank_account_returns_200(
    client, db_session, persist_user, make_auth_headers
):
    """A superadmin still deactivates a lower-rank account; the audit row names both ends."""
    superadmin = await persist_user(role=UserRole.superadmin)
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"is_active": False},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cedula"] == admin.cedula
    assert body["is_active"] is False

    await db_session.refresh(admin)
    assert admin.is_active is False

    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert len(audits) == 1
    assert audits[0].action == AuditAction.UPDATE
    assert audits[0].entity_id == admin.cedula
    assert audits[0].performed_by == superadmin.cedula
    assert audits[0].changes == {"is_active": False}


# --- BE-36 regression: a superadmin reactivates a peer superadmin, and nothing else ---

BE36_PASSWORD = "Password123"


async def test_be36_recovered_superadmin_reactivated_by_peer_can_log_in(
    client, db_session, persist_user, make_auth_headers
):
    """Round trip of the row: recover, the peer reactivates, the recovered one logs in."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(
        role=UserRole.superadmin,
        is_active=False,
        deleted_at=datetime.now(UTC),
        password_hash=get_password_hash(BE36_PASSWORD),
    )
    headers = make_auth_headers(superadmin)
    credentials = {"email": peer.email, "password": BE36_PASSWORD}

    recovered = await client.patch(f"/usuarios/{peer.cedula}/recuperar", headers=headers)
    login_before = await client.post("/usuarios/login", json=credentials)
    reactivated = await client.patch(
        f"/usuarios/{peer.cedula}", json={"is_active": True}, headers=headers
    )
    login_after = await client.post("/usuarios/login", json=credentials)

    assert recovered.status_code == 200
    assert login_before.status_code == 403
    assert reactivated.status_code == 200
    body = reactivated.json()
    assert body["cedula"] == peer.cedula
    assert body["role"] == "superadmin"
    assert body["is_active"] is True
    assert login_after.status_code == 200
    assert set(login_after.json()) == {"access_token", "token_type"}

    await db_session.refresh(peer)
    assert peer.deleted_at is None
    assert peer.is_active is True
    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
    assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
        (AuditAction.RECOVER, peer.cedula, superadmin.cedula, None),
        (AuditAction.UPDATE, peer.cedula, superadmin.cedula, {"is_active": True}),
    ]


async def test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in(
    client, db_session, persist_user, make_auth_headers
):
    """Second door: a superadmin created without is_active is born inactive; a peer fixes it."""
    superadmin = await persist_user(role=UserRole.superadmin)
    headers = make_auth_headers(superadmin)
    payload = {
        "cedula": "777777",
        "email": "newsuper@test.com",
        "first_name": "Nuevo",
        "last_name": "Super",
        "phone": "3000000000",
        "password": BE36_PASSWORD,
        "role": "superadmin",
        "data_consent": True,
    }
    credentials = {"email": payload["email"], "password": BE36_PASSWORD}

    created = await client.post("/usuarios/admin", json=payload, headers=headers)
    login_before = await client.post("/usuarios/login", json=credentials)
    reactivated = await client.patch("/usuarios/777777", json={"is_active": True}, headers=headers)
    login_after = await client.post("/usuarios/login", json=credentials)

    assert created.status_code == 201
    assert created.json()["is_active"] is False
    assert login_before.status_code == 403
    assert reactivated.status_code == 200
    assert reactivated.json()["is_active"] is True
    assert login_after.status_code == 200
    assert set(login_after.json()) == {"access_token", "token_type"}

    provisioned = (
        await db_session.execute(select(User).where(User.cedula == "777777"))
    ).scalar_one()
    assert provisioned.role == UserRole.superadmin
    assert provisioned.is_active is True
    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
    assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
        (AuditAction.CREATE, "777777", superadmin.cedula, {"role": "superadmin"}),
        (AuditAction.UPDATE, "777777", superadmin.cedula, {"is_active": True}),
    ]


@pytest.mark.parametrize(
    "payload",
    [{"is_active": True, "first_name": "Changed"}, {"first_name": "Changed"}, {"role": "admin"}],
    ids=["with-profile-field", "profile-only", "role-only"],
)
async def test_be36_peer_superadmin_update_other_than_reactivation_returns_403(
    client, db_session, persist_user, make_auth_headers, payload
):
    """Any other key, alone or next to is_active true, is still 403; nothing is written."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin, is_active=False)

    response = await client.patch(
        f"/usuarios/{peer.cedula}", json=payload, headers=make_auth_headers(superadmin)
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(peer)
    assert peer.is_active is False
    assert peer.first_name == "John"
    assert peer.role == UserRole.superadmin
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be36_peer_superadmin_deactivation_still_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """The exception reads the value: is_active false on a peer is still 403 (ADR-0017)."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": False},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(peer)
    assert peer.is_active is True
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be36_peer_still_in_recycle_bin_reactivation_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """Reactivation does not skip the recovery: a peer still in the recycle bin stays 403."""
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(
        role=UserRole.superadmin, is_active=False, deleted_at=datetime.now(UTC)
    )

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": True},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(peer)
    assert peer.is_active is False
    assert peer.deleted_at is not None
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be36_admin_reactivating_peer_admin_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """The exception is only between superadmins: an admin reactivating a peer admin gets 403."""
    admin = await persist_user(role=UserRole.admin)
    peer = await persist_user(role=UserRole.admin, is_active=False)

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": True},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert set(response.json()) == {"detail"}

    await db_session.refresh(peer)
    assert peer.is_active is False
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be36_superadmin_reactivating_active_peer_returns_200(
    client, db_session, persist_user, make_auth_headers
):
    """The exception does not read the current state: an active peer still gets 200.

    The audit row this no-op writes is BE-38 and is not frozen here.
    """
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": True},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cedula"] == peer.cedula
    assert body["role"] == "superadmin"
    assert body["is_active"] is True

    await db_session.refresh(peer)
    assert peer.is_active is True
    assert peer.deleted_at is None
    assert peer.role == UserRole.superadmin


# --- BE-58 regression: an administrative account never deletes or deactivates itself ---


async def test_be58_admin_self_delete_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """An admin DELETEing their own account gets 403; nothing is written (ADR-0019)."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.delete(
        f"/usuarios/{admin.cedula}",
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(admin)
    assert admin.deleted_at is None
    assert admin.is_active is True
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


@pytest.mark.parametrize(
    "payload",
    [{"is_active": False}, {"is_active": False, "first_name": "Changed"}],
    ids=["false", "with-profile-field"],
)
async def test_be58_admin_self_deactivation_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers, payload
):
    """An admin PATCHing their own is_active to false gets 403; no field changes (ADR-0019)."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json=payload,
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(admin)
    assert admin.is_active is True
    assert admin.first_name == "John"
    assert admin.deleted_at is None
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert audits == []


async def test_be58_admin_keeps_access_after_rejected_self_removal(
    client, db_session, persist_user, make_auth_headers
):
    """After both self-removals are rejected, the admin's same token still reads its profile."""
    admin = await persist_user(role=UserRole.admin)
    headers = make_auth_headers(admin)

    deleted = await client.delete(f"/usuarios/{admin.cedula}", headers=headers)
    deactivated = await client.patch(
        f"/usuarios/{admin.cedula}", json={"is_active": False}, headers=headers
    )
    profile = await client.get("/usuarios/mi-perfil", headers=headers)

    assert deleted.status_code == 403
    assert deactivated.status_code == 403
    assert profile.status_code == 200
    body = profile.json()
    assert body["cedula"] == admin.cedula
    assert body["role"] == "admin"
    assert body["is_active"] is True

    await db_session.refresh(admin)
    assert admin.deleted_at is None
    assert admin.is_active is True


async def test_be58_admin_self_update_with_is_active_true_returns_200(
    client, db_session, persist_user, make_auth_headers
):
    """The guard reads the value: is_active true on an admin's own account still succeeds."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"is_active": True},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cedula"] == admin.cedula
    assert body["is_active"] is True

    await db_session.refresh(admin)
    assert admin.is_active is True


# ==========================================
# C. GLOBAL EXCEPTION HANDLER TESTS
# ==========================================


async def test_authorization_error_maps_to_403_with_detail_key():
    """The unified domain handler maps AuthorizationError to a 403 JSON with a detail key."""
    request = Request(
        scope={
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "root_path": "",
            "headers": [(b"host", b"testserver")],
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "app": app,
        }
    )

    response = await domain_error_handler(request, AuthorizationError())

    assert response.status_code == 403
    body = json.loads(response.body)
    assert "detail" in body
    assert isinstance(body["detail"], str)


async def test_service_authorization_error_propagates_to_403_through_global_handler(
    client, persist_user, make_auth_headers
):
    """An AuthorizationError raised by the service layer surfaces as 403 with a detail key."""
    actor = await persist_user(role=UserRole.tourist)

    fake_service = create_autospec(UserService, instance=True)
    fake_service.delete_user_account.side_effect = AuthorizationError()

    app.dependency_overrides[get_user_service] = lambda: fake_service
    try:
        response = await client.delete(
            f"/usuarios/{actor.cedula}",
            headers=make_auth_headers(actor),
        )
    finally:
        app.dependency_overrides.pop(get_user_service, None)

    assert response.status_code == 403
    body = response.json()
    assert "detail" in body
