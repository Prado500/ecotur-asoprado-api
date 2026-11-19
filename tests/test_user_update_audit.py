"""Tests for BE-38: PATCH /usuarios/{cedula} audits only what changes, as old and new values.

changed_fields compares each validated value with the stored one after the access policy
(ADR-0021): a request that changes nothing answers 200 as before and writes no audit row, and
a partial change audits only the changed field. The policy still decides on the keys sent, so
an unchanged key it forbids is still a 403 (BE-02, ADR-0018).
"""

import pytest
from sqlalchemy import select

from app.models.audit import AuditAction, AuditLog
from app.models.user import User, UserRole


async def _audit_rows(db_session) -> list[AuditLog]:
    """Returns every audit row written so far, oldest first."""
    result = await db_session.execute(select(AuditLog).order_by(AuditLog.id))
    return list(result.scalars().all())


def _profile(user: User) -> tuple:
    """Returns the columns a PATCH can change, to compare them before and after."""
    return (user.email, user.first_name, user.last_name, user.phone, user.role, user.is_active)


@pytest.mark.parametrize(
    ("actor_role", "target_role", "payload"),
    [
        pytest.param(UserRole.superadmin, UserRole.admin, {"role": "admin"}, id="role-same"),
        pytest.param(UserRole.tourist, None, {"first_name": "John"}, id="first-name-same"),
        pytest.param(
            UserRole.admin, UserRole.tourist, {"first_name": "jOHN"}, id="first-name-normalized"
        ),
        pytest.param(UserRole.tourist, None, {"phone": None}, id="phone-null-already-null"),
        pytest.param(UserRole.admin, UserRole.tourist, {"is_active": True}, id="is-active-same"),
        pytest.param(
            UserRole.superadmin,
            UserRole.admin,
            {"role": "admin", "is_active": True, "first_name": "John", "last_name": "Doe"},
            id="four-keys-same",
        ),
    ],
)
async def test_be38_unchanged_user_update_returns_200_without_audit_row(
    client, db_session, persist_user, make_auth_headers, actor_role, target_role, payload
):
    """Edge case: every key sent already holds its value; 200, nothing changes, no audit row."""
    actor = await persist_user(role=actor_role)
    target = actor if target_role is None else await persist_user(role=target_role)
    before = _profile(target)

    response = await client.patch(
        f"/usuarios/{target.cedula}", json=payload, headers=make_auth_headers(actor)
    )

    assert response.status_code == 200
    assert response.json()["cedula"] == target.cedula
    await db_session.refresh(target)
    assert _profile(target) == before
    assert await _audit_rows(db_session) == []


async def test_be38_email_in_another_case_is_unchanged(
    client, db_session, persist_user, make_auth_headers
):
    """Edge case: the schema lowercases the email (ADR-0016), so the same address is no change."""
    tourist = await persist_user()
    stored_email = tourist.email

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"email": stored_email.upper()},
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 200
    assert response.json()["email"] == stored_email
    await db_session.refresh(tourist)
    assert tourist.email == stored_email
    assert await _audit_rows(db_session) == []


async def test_be38_partial_change_audits_only_the_changed_field(
    client, db_session, persist_user, make_auth_headers
):
    """Happy path: of two keys sent, only the changed one is audited, with its old value."""
    superadmin = await persist_user(role=UserRole.superadmin)
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"first_name": "John", "last_name": "Nuevo"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 200
    assert response.json()["last_name"] == "Nuevo"
    await db_session.refresh(admin)
    assert (admin.first_name, admin.last_name) == ("John", "Nuevo")
    audits = await _audit_rows(db_session)
    assert [(a.action, a.entity_id, a.performed_by, a.changes) for a in audits] == [
        (
            AuditAction.UPDATE,
            admin.cedula,
            superadmin.cedula,
            {"last_name": {"old": "Doe", "new": "Nuevo"}},
        )
    ]


async def test_be38_peer_reactivation_with_an_unchanged_extra_key_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: the policy reads the keys sent, not the ones that change (ADR-0018).

    first_name already holds its value; dropping it before the policy would turn this body
    into the bare reactivation that ADR-0018 allows.
    """
    superadmin = await persist_user(role=UserRole.superadmin)
    peer = await persist_user(role=UserRole.superadmin, is_active=False)

    response = await client.patch(
        f"/usuarios/{peer.cedula}",
        json={"is_active": True, "first_name": "John"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 403
    assert isinstance(response.json()["detail"], str)
    await db_session.refresh(peer)
    assert peer.is_active is False
    assert await _audit_rows(db_session) == []


async def test_be38_admin_self_role_with_unchanged_value_returns_403(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: the role key on one's own account is a 403 even with its value (BE-02)."""
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": "admin", "first_name": "Otro"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    assert isinstance(response.json()["detail"], str)
    await db_session.refresh(admin)
    assert admin.first_name == "John"
    assert await _audit_rows(db_session) == []
