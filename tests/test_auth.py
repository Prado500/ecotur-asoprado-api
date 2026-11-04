from datetime import UTC, datetime
from typing import Any
from unittest.mock import ANY

import jwt
from sqlalchemy import func, select

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
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


async def test_actualizacion_perfil_self_service_exitoso(client, db_session):
    """
    Validates that a standard tourist can securely update their own basic profile data.
    """
    # 1. ARRANGE: Create and activate a Tourist
    await client.post("/usuarios/registro", json=USER_PAYLOAD)
    stmt = select(User).where(User.email == USER_PAYLOAD["email"])
    tourist = (await db_session.execute(stmt)).scalars().first()
    tourist.is_active = True
    await db_session.commit()

    # Generate Token
    token = create_access_token(data={"sub": tourist.email, "role": tourist.role.value})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. ACT: Send PATCH request with valid scalar fields
    update_payload = {"first_name": "Nombre Modificado"}
    response = await client.patch(
        f"/usuarios/{tourist.cedula}", json=update_payload, headers=headers
    )

    # 3. ASSERT: Response is successful and the mutation was persisted
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Nombre Modificado"
    assert data["role"] == "tourist"
    assert data["is_active"] is True

    await db_session.refresh(tourist)
    assert tourist.first_name == "Nombre Modificado"
    assert tourist.role == UserRole.tourist
    assert tourist.is_active is True


async def test_actualizacion_perfil_escalacion_rol_rechazada(client, db_session):
    """
    Validates the fail-safe invariant: a tourist attempting to mutate 'role'
    is rejected with HTTP 403 and the role remains unchanged in the database.
    """
    # 1. ARRANGE: Create and activate a Tourist
    await client.post("/usuarios/registro", json=USER_PAYLOAD)
    stmt = select(User).where(User.email == USER_PAYLOAD["email"])
    tourist = (await db_session.execute(stmt)).scalars().first()
    tourist.is_active = True
    await db_session.commit()

    token = create_access_token(data={"sub": tourist.email, "role": tourist.role.value})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. ACT: Malicious escalation attempt
    update_payload = {"role": "superadmin"}
    response = await client.patch(
        f"/usuarios/{tourist.cedula}", json=update_payload, headers=headers
    )

    # 3. ASSERT: Loud rejection without any state mutation
    assert response.status_code == 403
    assert "detail" in response.json()

    await db_session.refresh(tourist)
    assert tourist.role == UserRole.tourist


async def test_actualizacion_perfil_mutacion_estado_rechazada(client, db_session):
    """
    Validates the fail-safe invariant: a tourist attempting to mutate 'is_active'
    is rejected with HTTP 403 and the active state remains unchanged.
    """
    # 1. ARRANGE: Create and activate a Tourist
    await client.post("/usuarios/registro", json=USER_PAYLOAD)
    stmt = select(User).where(User.email == USER_PAYLOAD["email"])
    tourist = (await db_session.execute(stmt)).scalars().first()
    tourist.is_active = True
    await db_session.commit()

    token = create_access_token(data={"sub": tourist.email, "role": tourist.role.value})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. ACT: Malicious status mutation attempt
    update_payload = {"is_active": False}
    response = await client.patch(
        f"/usuarios/{tourist.cedula}", json=update_payload, headers=headers
    )

    # 3. ASSERT: Loud rejection without any state mutation
    assert response.status_code == 403
    assert "detail" in response.json()

    await db_session.refresh(tourist)
    assert tourist.is_active is True


async def test_actualizacion_usuario_helpdesk_exitoso(client, db_session):
    """
    Validates the Helpdesk pattern: An Admin can update a Tourist's account.
    """
    # 1. ARRANGE: Create Admin
    admin = User(
        cedula="999999999",
        email="admin@asoprado.com",
        first_name="Admin",
        last_name="Test",
        password_hash=get_password_hash("pass"),
        role=UserRole.admin,
        is_active=True,
        data_consent=True,
    )
    db_session.add(admin)

    # ARRANGE: Create Tourist
    tourist = User(
        cedula="111111111",
        email="turista2@asoprado.com",
        first_name="Juan",
        last_name="Test",
        password_hash=get_password_hash("pass"),
        role=UserRole.tourist,
        is_active=True,
        data_consent=True,
    )
    db_session.add(tourist)
    await db_session.commit()

    admin_token = create_access_token(data={"sub": admin.email, "role": admin.role.value})

    # 2. ACT: Admin updates Tourist's email
    update_payload = {"email": "correo_corregido@asoprado.com"}
    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json=update_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 3. ASSERT
    assert response.status_code == 200
    assert response.json()["email"] == "correo_corregido@asoprado.com"


async def test_actualizacion_usuario_violacion_jerarquia(client, db_session):
    """
    Validates hierarchical precedence rules: An Admin MUST NOT be able to modify
    the account of a Superadmin (403 Forbidden).
    """
    # 1. ARRANGE: Create Admin and Superadmin
    admin = User(
        cedula="888888888",
        email="admin2@asoprado.com",
        first_name="Admin",
        last_name="Test",
        password_hash=get_password_hash("pass"),
        role=UserRole.admin,
        is_active=True,
        data_consent=True,
    )
    superadmin = User(
        cedula="000000000",
        email="super@asoprado.com",
        first_name="Super",
        last_name="Test",
        password_hash=get_password_hash("pass"),
        role=UserRole.superadmin,
        is_active=True,
        data_consent=True,
    )
    db_session.add_all([admin, superadmin])
    await db_session.commit()

    admin_token = create_access_token(data={"sub": admin.email, "role": admin.role.value})

    # 2. ACT: Admin attempts to update Superadmin
    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"first_name": "Hacked"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 3. ASSERT
    assert response.status_code == 403
    assert "Violación de jerarquía" in response.json()["detail"]


async def test_listar_usuarios_visibilidad_jerarquica(client, db_session):
    """
    Validates dynamic directory visibility. A standard Admin requesting the user
    list should receive Tourists and Admins, but Superadmins must be completely obscured.
    """
    # 1. ARRANGE: Create 1 of each role
    u1 = User(
        cedula="111111",
        email="t@t.com",
        first_name="Tania",
        last_name="Torres",
        password_hash="x",
        role=UserRole.tourist,
        is_active=True,
        data_consent=True,
    )
    u2 = User(
        cedula="222222",
        email="a@a.com",
        first_name="Anastasia",
        last_name="Andrade",
        password_hash="x",
        role=UserRole.admin,
        is_active=True,
        data_consent=True,
    )
    u3 = User(
        cedula="333333",
        email="s@s.com",
        first_name="Sofia",
        last_name="Sanchez",
        password_hash="x",
        role=UserRole.superadmin,
        is_active=True,
        data_consent=True,
    )

    db_session.add_all([u1, u2, u3])
    await db_session.commit()

    admin_token = create_access_token(data={"sub": u2.email, "role": u2.role.value})

    # 2. ACT: Admin fetches user directory
    response = await client.get("/usuarios/", headers={"Authorization": f"Bearer {admin_token}"})

    # 3. ASSERT
    assert response.status_code == 200
    data = response.json()
    roles_returned = [user["role"] for user in data]

    assert "tourist" in roles_returned
    assert "admin" in roles_returned
    assert "superadmin" not in roles_returned  # Obscured successfully


async def test_listar_usuarios_eliminados_visibilidad(client, db_session):
    """
    Validates dynamic directory visibility for the Recycle Bin.
    A standard Admin requesting the deleted user list should receive deleted
    Tourists, but deleted Superadmins must be completely obscured.
    """
    # 1. ARRANGE: Create users and soft-delete some of them
    admin = User(
        cedula="999999",
        email="admin101@test.com",
        first_name="Marisol",
        last_name="Gutierrez",
        password_hash="x",
        role=UserRole.admin,
        is_active=True,
        data_consent=True,
    )
    deleted_tourist = User(
        cedula="888888",
        email="tourist102@test.com",
        first_name="Antonio",
        last_name="Delgado",
        password_hash="x",
        role=UserRole.tourist,
        is_active=False,
        data_consent=True,
        deleted_at=datetime.now(UTC),
    )
    deleted_super = User(
        cedula="777777",
        email="super103@test.com",
        first_name="Jose",
        last_name="Flores",
        password_hash="x",
        role=UserRole.superadmin,
        is_active=False,
        data_consent=True,
        deleted_at=datetime.now(UTC),
    )

    db_session.add_all([admin, deleted_tourist, deleted_super])
    await db_session.commit()

    admin_token = create_access_token(data={"sub": admin.email, "role": admin.role.value})

    # 2. ACT: Admin fetches deleted user directory
    response = await client.get(
        "/usuarios/admin/eliminados", headers={"Authorization": f"Bearer {admin_token}"}
    )

    # 3. ASSERT
    assert response.status_code == 200
    data = response.json()
    cedulas_returned = [user["cedula"] for user in data]

    assert "888888" in cedulas_returned  # Tourist is visible
    assert "777777" not in cedulas_returned  # Superadmin is mathematically obscured


async def test_recuperar_usuario_exitoso(client, db_session):
    """
    Validates the Helpdesk recovery pattern: An Admin can recover a Tourist's account.
    Asserts that the recovered account transitions to an inactive state by default.
    """
    # 1. ARRANGE: Create Admin and a soft-deleted Tourist
    admin = User(
        cedula="111111",
        email="admin201@test.com",
        first_name="Andres",
        last_name="Angarita",
        password_hash="x",
        role=UserRole.admin,
        is_active=True,
        data_consent=True,
    )
    tourist = User(
        cedula="222222",
        email="tourist202@test.com",
        first_name="Tulio",
        last_name="Torres",
        password_hash="x",
        role=UserRole.tourist,
        is_active=False,
        data_consent=True,
        deleted_at=datetime.now(UTC),
    )

    db_session.add_all([admin, tourist])
    await db_session.commit()

    admin_token = create_access_token(data={"sub": admin.email, "role": admin.role.value})

    # 2. ACT: Admin recovers Tourist
    response = await client.patch(
        f"/usuarios/{tourist.cedula}/recuperar", headers={"Authorization": f"Bearer {admin_token}"}
    )

    # 3. ASSERT
    assert response.status_code == 200
    assert response.json()["success"] is True

    await db_session.refresh(tourist)
    assert tourist.deleted_at is None
    assert tourist.is_active is False  # Strict security rule enforced


async def test_recuperar_usuario_violacion_jerarquia(client, db_session):
    """
    Validates hierarchical precedence rules during recovery: An Admin MUST NOT
    be able to recover the account of a soft-deleted Superadmin (403 Forbidden).
    """
    # 1. ARRANGE: Create Admin and a soft-deleted Superadmin
    admin = User(
        cedula="111111",
        email="admin301@test.com",
        first_name="Arnulfo",
        last_name="Anzoátegui",
        password_hash="x",
        role=UserRole.admin,
        is_active=True,
        data_consent=True,
    )
    superadmin = User(
        cedula="222222",
        email="super302@test.com",
        first_name="Sandra",
        last_name="Sanchez",
        password_hash="x",
        role=UserRole.superadmin,
        is_active=False,
        data_consent=True,
        deleted_at=datetime.now(UTC),
    )

    db_session.add_all([admin, superadmin])
    await db_session.commit()

    admin_token = create_access_token(data={"sub": admin.email, "role": admin.role.value})

    # 2. ACT: Admin attempts to recover Superadmin
    response = await client.patch(
        f"/usuarios/{superadmin.cedula}/recuperar",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 3. ASSERT
    assert response.status_code == 403
    assert "jerarquía" in response.json()["detail"].lower()


async def test_crear_administrador_violacion_jerarquia(client, db_session):
    """
    Validates that standard Admins cannot provision new administrative accounts (403 Forbidden).
    """
    # 1. ARRANGE: Create standard Admin
    admin = User(
        cedula="111111",
        email="admin401@test.com",
        first_name="Amelio",
        last_name="Ardiles",
        password_hash="x",
        role=UserRole.admin,
        is_active=True,
        data_consent=True,
    )
    db_session.add(admin)
    await db_session.commit()

    admin_token = create_access_token(data={"sub": admin.email, "role": admin.role.value})

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

    # 2. ACT: Standard Admin tries to create another Admin
    response = await client.post(
        "/usuarios/admin",
        json=new_admin_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # 3. ASSERT
    assert response.status_code == 403
    assert "superusuario" in response.json()["detail"].lower()


async def test_crear_administrador_exitoso(client, db_session):
    """
    Validates that a Superadmin can successfully provision new administrative accounts.
    """
    # 1. ARRANGE: Create Superadmin
    superadmin = User(
        cedula="666666",
        email="super501@test.com",
        first_name="Federico",
        last_name="Perez",
        password_hash="x",
        role=UserRole.superadmin,
        is_active=True,
        data_consent=True,
    )
    db_session.add(superadmin)
    await db_session.commit()

    super_token = create_access_token(data={"sub": superadmin.email, "role": superadmin.role.value})

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

    # 2. ACT: Superadmin creates an Admin
    response = await client.post(
        "/usuarios/admin",
        json=new_admin_payload,
        headers={"Authorization": f"Bearer {super_token}"},
    )

    # 3. ASSERT
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "admin"
    assert data["cedula"] == "555555"
    assert data["is_active"] is True
