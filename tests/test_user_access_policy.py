"""Test suite for the extracted UserAccessPolicy authorization rules.

Freezes the pure hierarchical ABAC invariants at the domain-policy level
(unit tests), the transport-domain contract through the real HTTP stack
(integration tests), and the AuthorizationError -> HTTP 403 mapping
(global-handler tests).
"""

import json
from unittest.mock import create_autospec

import pytest
from sqlalchemy.future import select
from starlette.requests import Request

from app.api.dependencies import get_user_service
from app.core.exceptions import AuthorizationError
from app.main import app, authorization_error_handler
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
    """Freezes the deletion invariant: self-parity or strictly higher rank."""

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

    def test_superadmin_self_delete_is_allowed(self, policy, make_user):
        superadmin = make_user(role=UserRole.superadmin)

        policy.assert_can_delete(superadmin, superadmin)

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
    """Freezes update invariants: hierarchy parity, role fail-safe and is_active fail-safe."""

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


class TestAssertCanProvisionAdmin:
    """Freezes provisioning governance: only superadmins create administrative accounts."""

    def test_superadmin_can_provision_admin(self, policy, make_user):
        actor = make_user(role=UserRole.superadmin)

        policy.assert_can_provision_admin(actor)

    def test_admin_cannot_provision_admin(self, policy, make_user):
        actor = make_user(role=UserRole.admin)

        with pytest.raises(AuthorizationError):
            policy.assert_can_provision_admin(actor)

    def test_tourist_cannot_provision_admin(self, policy, make_user):
        actor = make_user(role=UserRole.tourist)

        with pytest.raises(AuthorizationError):
            policy.assert_can_provision_admin(actor)


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


async def test_patch_hierarchy_violation_returns_403_detail(client, db_session, persist_user, make_auth_headers):
    """Admin patching a superadmin yields 403 with the detail key and zero state mutation."""
    admin = await persist_user(role=UserRole.admin)
    superadmin = await persist_user(role=UserRole.superadmin)

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"first_name": "Hacked"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert "detail" in response.json()

    await db_session.refresh(superadmin)
    assert superadmin.first_name == "John"


async def test_delete_hierarchy_violation_returns_403_detail(client, db_session, persist_user, make_auth_headers):
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


async def test_patch_nonexistent_cedula_returns_404_before_403(client, persist_user, make_auth_headers):
    """Order invariant: 404 (existence) precedes 403 (permissions) on PATCH."""
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        "/usuarios/9999999999",
        json={"first_name": "Ghost"},
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_delete_nonexistent_cedula_returns_404_before_403(client, persist_user, make_auth_headers):
    """Order invariant: 404 (existence) precedes 403 (permissions) on DELETE."""
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.delete(
        "/usuarios/9999999999",
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_admin_cannot_provision_admin_account_403_and_no_db_mutation(client, db_session, persist_user, make_auth_headers):
    """Proxy-person escalation: admin provisioning an admin account yields 403 and persists nothing."""
    admin = await persist_user(role=UserRole.admin)

    payload = {
        "cedula": "5555555555",
        "email": "newadmin@test.com",
        "first_name": "New",
        "last_name": "Admin",
        "phone": "3000000000",
        "password": "Password123",
        "role": "admin",
        "data_consent": True,
        "is_active": True,
    }

    response = await client.post("/usuarios/admin", json=payload, headers=make_auth_headers(admin))

    assert response.status_code == 403
    assert "detail" in response.json()

    users = (await db_session.execute(select(User))).scalars().all()
    assert len(users) == 1
    assert users[0].cedula == admin.cedula


async def test_admin_update_tourist_persists_mutation(client, db_session, persist_user, make_auth_headers):
    """Successful helpdesk PATCH persists the scalar mutation in the database."""
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"email": "corrected@test.com"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 200
    assert response.json()["email"] == "corrected@test.com"

    await db_session.refresh(tourist)
    assert tourist.email == "corrected@test.com"


async def test_admin_cannot_escalate_tourist_to_superadmin_via_patch(client, db_session, persist_user, make_auth_headers):
    """Two-step proxy escalation: admin promoting a tourist to superadmin yields 403 with no mutation."""
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


async def test_admin_cannot_escalate_tourist_to_admin_via_patch(client, db_session, persist_user, make_auth_headers):
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


# ==========================================
# C. GLOBAL EXCEPTION HANDLER TESTS
# ==========================================


async def test_authorization_error_handler_returns_403_with_detail_key():
    """The global handler maps AuthorizationError to a 403 JSON with a detail key."""
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

    response = await authorization_error_handler(request, AuthorizationError())

    assert response.status_code == 403
    body = json.loads(response.body)
    assert "detail" in body
    assert isinstance(body["detail"], str)


async def test_service_authorization_error_propagates_to_403_through_global_handler(client, persist_user, make_auth_headers):
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
