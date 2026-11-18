"""Tests for BE-37: an explicit null on a NOT NULL user column is a 422 (ADR-0020).

UserUpdate rejects null on email, first_name, last_name, role and is_active before the access
policy runs, so the request changes nothing and writes no audit row. phone keeps accepting null,
which clears it, and an absent field still means "leave it as it is".
"""

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.models.audit import AuditLog
from app.models.user import UserRole
from app.schemas.user import UserUpdate


async def _audit_rows(db_session) -> list[AuditLog]:
    """Returns every audit row written so far."""
    return list((await db_session.execute(select(AuditLog))).scalars().all())


def test_be37_absent_fields_stay_unset() -> None:
    """Edge case: an empty payload sets nothing; absent is not null."""
    update = UserUpdate.model_validate({})

    assert update.model_dump(exclude_unset=True) == {}
    assert update.role is None
    assert update.is_active is None


def test_be37_every_null_field_is_reported() -> None:
    """Edge case: two nulls give two errors, and the valid field beside them does not save them."""
    with pytest.raises(ValidationError) as exc_info:
        UserUpdate.model_validate({"role": None, "is_active": None, "first_name": "Nuevo"})

    assert [error["loc"] for error in exc_info.value.errors()] == [("role",), ("is_active",)]


@pytest.mark.parametrize(
    ("actor_role", "target_role", "field"),
    [
        pytest.param(UserRole.superadmin, UserRole.admin, "email", id="superadmin-on-admin-email"),
        pytest.param(
            UserRole.superadmin, UserRole.admin, "first_name", id="superadmin-on-admin-first_name"
        ),
        pytest.param(
            UserRole.superadmin, UserRole.admin, "last_name", id="superadmin-on-admin-last_name"
        ),
        pytest.param(UserRole.superadmin, UserRole.admin, "role", id="superadmin-on-admin-role"),
        pytest.param(
            UserRole.superadmin, UserRole.admin, "is_active", id="superadmin-on-admin-is_active"
        ),
        pytest.param(UserRole.superadmin, None, "role", id="superadmin-on-self-role"),
        pytest.param(UserRole.admin, UserRole.tourist, "role", id="admin-on-tourist-role"),
        pytest.param(UserRole.tourist, None, "is_active", id="tourist-on-self-is_active"),
        pytest.param(
            UserRole.superadmin, UserRole.superadmin, "is_active", id="superadmin-on-peer-is_active"
        ),
    ],
)
async def test_be37_null_on_not_null_field_returns_422_without_mutation(
    client, db_session, persist_user, make_auth_headers, actor_role, target_role, field
):
    """Unhappy path: 422 naming the field; the account and the audit log stay as they were.

    The last four cases were a 403 of the access policy before BE-37; the null now stops at
    the schema, so the policy never sees it (ADR-0020; ADR-0018 addendum for the peer case).
    """
    actor = await persist_user(role=actor_role)
    target = actor if target_role is None else await persist_user(role=target_role)
    stored_before = getattr(target, field)

    response = await client.patch(
        f"/usuarios/{target.cedula}", json={field: None}, headers=make_auth_headers(actor)
    )

    assert response.status_code == 422
    errors = response.json()["detalle"]
    assert [error["raw_field"] for error in errors] == [field]
    assert isinstance(errors[0]["message"], str)
    await db_session.refresh(target)
    assert getattr(target, field) == stored_before
    assert await _audit_rows(db_session) == []


async def test_be37_null_beside_a_valid_field_changes_nothing(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: the valid first_name sent beside a null role is not saved either."""
    superadmin = await persist_user(role=UserRole.superadmin)
    admin = await persist_user(role=UserRole.admin)

    response = await client.patch(
        f"/usuarios/{admin.cedula}",
        json={"role": None, "first_name": "Nuevo"},
        headers=make_auth_headers(superadmin),
    )

    assert response.status_code == 422
    assert [error["raw_field"] for error in response.json()["detalle"]] == ["role"]
    await db_session.refresh(admin)
    assert admin.first_name == "John"
    assert admin.role == UserRole.admin
    assert await _audit_rows(db_session) == []


@pytest.mark.parametrize(
    ("actor_role", "target_role"),
    [
        pytest.param(UserRole.superadmin, UserRole.admin, id="superadmin-on-admin"),
        pytest.param(UserRole.tourist, None, id="tourist-on-self"),
    ],
)
async def test_be37_null_on_phone_still_clears_it(
    client, db_session, persist_user, make_auth_headers, actor_role, target_role
):
    """Happy path: the phone column admits empty, so null clears it and the change is audited."""
    actor = await persist_user(role=actor_role, phone="3001234567")
    target = (
        actor if target_role is None else await persist_user(role=target_role, phone="3001234567")
    )

    response = await client.patch(
        f"/usuarios/{target.cedula}", json={"phone": None}, headers=make_auth_headers(actor)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cedula"] == target.cedula
    assert body["phone"] is None
    await db_session.refresh(target)
    assert target.phone is None
    audits = await _audit_rows(db_session)
    assert [(audit.entity_id, audit.changes) for audit in audits] == [
        (target.cedula, {"phone": {"old": "3001234567", "new": None}})
    ]


async def test_be37_missing_token_is_rejected_before_the_null(client, db_session, persist_user):
    """Unhappy path: without a token the guard answers 401 before the body is validated."""
    tourist = await persist_user()

    response = await client.patch(f"/usuarios/{tourist.cedula}", json={"role": None})

    assert response.status_code == 401
    assert isinstance(response.json()["detail"], str)
    await db_session.refresh(tourist)
    assert tourist.role == UserRole.tourist
    assert await _audit_rows(db_session) == []
