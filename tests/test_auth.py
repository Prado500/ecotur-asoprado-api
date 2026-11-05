from datetime import UTC, datetime
from typing import Any
from unittest.mock import ANY

import jwt
from sqlalchemy import func, select

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_verification_token,
    get_password_hash,
)
from app.models.user import User, UserRole

USER_PAYLOAD: dict[str, Any] = {
    "cedula": "1005911792",
    "email": "turista@example.com",
    "first_name": "Juan",
    "last_name": "Perez",
    "phone": "3001234567",
    "password": "passwordSegura123",
    "data_consent": True,
}
PASSWORD = USER_PAYLOAD["password"]


async def test_register_tourist_returns_201_and_schedules_verification_email(
    client, db_session, mock_send_email
):
    """Registration creates an inactive tourist and schedules the verification email."""
    response = await client.post("/usuarios/registro", json=USER_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["first_name"] == USER_PAYLOAD["first_name"]
    assert "id" in data
    assert "password" not in data
    assert data["cedula"] == USER_PAYLOAD["cedula"]
    assert data["is_active"] is False

    mock_send_email.assert_called_once_with(
        email_to=USER_PAYLOAD["email"], first_name="Juan", token=ANY, base_url=ANY
    )

    stmt = select(User).where(User.cedula == USER_PAYLOAD["cedula"])
    user = (await db_session.execute(stmt)).scalar_one()
    assert user.is_active is False
    assert user.role == UserRole.tourist


async def test_register_duplicate_returns_400_without_second_row(
    client, db_session, mock_send_email
):
    """A second registration with the same data yields 400 and persists nothing new."""
    first = await client.post("/usuarios/registro", json=USER_PAYLOAD)
    assert first.status_code == 201

    response = await client.post("/usuarios/registro", json=USER_PAYLOAD)

    assert response.status_code == 400
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    count = await db_session.execute(select(func.count()).select_from(User))
    assert count.scalar_one() == 1

    mock_send_email.assert_called_once_with(
        email_to=USER_PAYLOAD["email"], first_name="Juan", token=ANY, base_url=ANY
    )


async def test_verify_email_endpoint_activates_account(client, db_session, persist_user):
    """A valid verification token activates the account behind it."""
    user = await persist_user(is_active=False)
    token = create_verification_token(user.email)

    response = await client.get(f"/usuarios/verificar-email?token={token}")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"success", "message"}
    assert body["success"] is True

    await db_session.refresh(user)
    assert user.is_active is True


async def test_verify_email_invalid_token_returns_400(client):
    """A malformed verification token yields 400 with the error shape."""
    response = await client.get("/usuarios/verificar-email?token=tokenFalso123")

    assert response.status_code == 400
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)


async def test_login_active_user_returns_bearer_token(client, persist_user):
    """An active account with the right password receives a bearer token with its claims."""
    user = await persist_user(password_hash=get_password_hash(PASSWORD), is_active=True)

    response = await client.post(
        "/usuarios/login", json={"email": user.email, "password": PASSWORD}
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"access_token", "token_type"}
    assert body["token_type"] == "bearer"

    assert SECRET_KEY is not None
    claims = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["sub"] == user.email
    assert claims["role"] == "tourist"


async def test_login_inactive_user_returns_403_without_token(client, persist_user):
    """An inactive account with the right password yields 403 and no token."""
    user = await persist_user(password_hash=get_password_hash(PASSWORD), is_active=False)

    response = await client.post(
        "/usuarios/login", json={"email": user.email, "password": PASSWORD}
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)


async def test_login_wrong_password_returns_401_with_bearer_challenge(client, persist_user):
    """A wrong password on an active account yields 401 with the Bearer challenge."""
    user = await persist_user(password_hash=get_password_hash(PASSWORD), is_active=True)

    response = await client.post(
        "/usuarios/login", json={"email": user.email, "password": "wrongPassword1"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)


async def test_self_soft_delete_keeps_row_and_blocks_login(
    client, db_session, persist_user, make_auth_headers
):
    """Self-deletion keeps the row, stamps deleted_at, deactivates it and blocks login."""
    user = await persist_user(password_hash=get_password_hash(PASSWORD), is_active=True)

    response = await client.delete(f"/usuarios/{user.cedula}", headers=make_auth_headers(user))

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"success", "message"}
    assert body["success"] is True
    assert isinstance(body["message"], str)

    await db_session.refresh(user)
    assert user.deleted_at is not None
    assert user.is_active is False

    login = await client.post("/usuarios/login", json={"email": user.email, "password": PASSWORD})
    assert login.status_code == 401


# ==========================================
# RBAC AND USER MANAGEMENT (U+D) TESTS
# ==========================================


async def test_tourist_self_update_persists_profile_change(
    client, db_session, persist_user, make_auth_headers
):
    """A tourist can update their own basic profile data, and the change is persisted."""
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"first_name": "Nombre Modificado"},
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Nombre Modificado"
    assert data["role"] == "tourist"
    assert data["is_active"] is True

    await db_session.refresh(tourist)
    assert tourist.first_name == "Nombre Modificado"
    assert tourist.role == UserRole.tourist
    assert tourist.is_active is True


async def test_tourist_self_role_escalation_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """A tourist sending a role change on their own account gets 403; the role stays."""
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"role": "superadmin"},
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(tourist)
    assert tourist.role == UserRole.tourist


async def test_tourist_self_is_active_change_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """A tourist sending an is_active change on their own account gets 403; the state stays."""
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"is_active": False},
        headers=make_auth_headers(tourist),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(tourist)
    assert tourist.is_active is True


async def test_admin_updates_tourist_email_and_persists_it(
    client, db_session, persist_user, make_auth_headers
):
    """An admin can correct a tourist's email (helpdesk), and the change is persisted."""
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"email": "correo_corregido@asoprado.com"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 200
    assert response.json()["email"] == "correo_corregido@asoprado.com"

    await db_session.refresh(tourist)
    assert tourist.email == "correo_corregido@asoprado.com"


async def test_admin_patching_superadmin_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """An admin cannot modify a superadmin's account: 403 and no change in the database."""
    admin = await persist_user(role=UserRole.admin)
    superadmin = await persist_user(role=UserRole.superadmin)
    original_first_name = superadmin.first_name

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"first_name": "Hacked"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(superadmin)
    assert superadmin.first_name == original_first_name


async def test_admin_directory_hides_superadmins(client, persist_user, make_auth_headers):
    """An admin's user directory lists tourists and admins, never superadmins."""
    tourist = await persist_user(role=UserRole.tourist)
    admin = await persist_user(role=UserRole.admin)
    await persist_user(role=UserRole.superadmin)

    response = await client.get("/usuarios/", headers=make_auth_headers(admin))

    assert response.status_code == 200
    body = response.json()
    assert {u["cedula"] for u in body} == {tourist.cedula, admin.cedula}


async def test_admin_deleted_directory_hides_deleted_superadmins(
    client, persist_user, make_auth_headers
):
    """An admin's recycle bin lists deleted tourists, never deleted superadmins."""
    admin = await persist_user(role=UserRole.admin)
    deleted_tourist = await persist_user(
        role=UserRole.tourist, is_active=False, deleted_at=datetime.now(UTC)
    )
    await persist_user(role=UserRole.superadmin, is_active=False, deleted_at=datetime.now(UTC))

    response = await client.get("/usuarios/admin/eliminados", headers=make_auth_headers(admin))

    assert response.status_code == 200
    body = response.json()
    assert [u["cedula"] for u in body] == [deleted_tourist.cedula]


async def test_admin_recovers_tourist_as_inactive(
    client, db_session, persist_user, make_auth_headers
):
    """An admin can recover a deleted tourist; the account comes back inactive."""
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(
        role=UserRole.tourist, is_active=False, deleted_at=datetime.now(UTC)
    )

    response = await client.patch(
        f"/usuarios/{tourist.cedula}/recuperar", headers=make_auth_headers(admin)
    )

    assert response.status_code == 200
    body = response.json()
    assert {"success", "message"} <= set(body)
    assert body["success"] is True
    assert isinstance(body["message"], str)

    await db_session.refresh(tourist)
    assert tourist.deleted_at is None
    assert tourist.is_active is False


async def test_admin_recovering_superadmin_returns_403_without_mutation(
    client, db_session, persist_user, make_auth_headers
):
    """An admin cannot recover a deleted superadmin: 403 and the account stays deleted."""
    admin = await persist_user(role=UserRole.admin)
    superadmin = await persist_user(
        role=UserRole.superadmin, is_active=False, deleted_at=datetime.now(UTC)
    )

    response = await client.patch(
        f"/usuarios/{superadmin.cedula}/recuperar", headers=make_auth_headers(admin)
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    await db_session.refresh(superadmin)
    assert superadmin.deleted_at is not None


async def test_admin_provisioning_admin_returns_403_without_row(
    client, db_session, persist_user, make_auth_headers
):
    """A standard admin cannot provision an admin account: 403 and no new row."""
    admin = await persist_user(role=UserRole.admin)

    new_admin_payload = {
        "cedula": "222222",
        "email": "newadmin@test.com",
        "first_name": "Federico",
        "last_name": "Murcia",
        "phone": "3000000000",
        "password": "Password123",
        "role": "admin",
        "data_consent": True,
        "is_active": True,
    }

    response = await client.post(
        "/usuarios/admin", json=new_admin_payload, headers=make_auth_headers(admin)
    )

    assert response.status_code == 403
    body = response.json()
    assert set(body) == {"detail"}
    assert isinstance(body["detail"], str)

    count = await db_session.execute(select(func.count()).select_from(User))
    assert count.scalar_one() == 1


async def test_superadmin_provisions_admin_account(
    client, db_session, persist_user, make_auth_headers
):
    """A superadmin can provision a new, active admin account."""
    superadmin = await persist_user(role=UserRole.superadmin)

    new_admin_payload = {
        "cedula": "555555",
        "email": "newadmin502@test.com",
        "first_name": "New",
        "last_name": "Admin",
        "phone": "3000000000",
        "password": "Password123",
        "role": "admin",
        "data_consent": True,
        "is_active": True,
    }

    response = await client.post(
        "/usuarios/admin", json=new_admin_payload, headers=make_auth_headers(superadmin)
    )

    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "admin"
    assert data["cedula"] == "555555"
    assert data["is_active"] is True

    result = await db_session.execute(select(User).where(User.cedula == "555555"))
    created = result.scalar_one()
    await db_session.refresh(created)
    assert created.role == UserRole.admin
    assert created.is_active is True
    assert created.deleted_at is None
