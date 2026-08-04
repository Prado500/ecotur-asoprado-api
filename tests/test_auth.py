from unittest.mock import patch

import pytest
from sqlalchemy.future import select

from app.core.security import create_verification_token, create_access_token, get_password_hash
from app.models.user import User, UserRole

USER_PAYLOAD = {
    "cedula": "1005911792",
    "email": "turista@example.com",
    "first_name": "Juan",
    "last_name": "Perez",
    "phone": "3001234567",
    "password": "passwordSegura123",
    "data_consent": True
}

# === PREVENT ACTUAL EMAIL DISPATCH DURING TESTS ===
@pytest.fixture(autouse=True)
def mock_send_email():
    """
    Intercepts the email dispatch function within UserService to avoid
    SMTP connection exceptions and accelerate test execution.
    """
    with patch("app.services.user_service.send_verification_email") as mock:
        yield mock

async def test_registro_usuario_exitoso(client, mock_send_email):
    """Test that a new user can successfully register and triggers the email task."""
    response = await client.post("/usuarios/registro", json=USER_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["first_name"] == USER_PAYLOAD["first_name"]
    assert "id" in data
    assert "password" not in data
    assert data["cedula"] == USER_PAYLOAD["cedula"]
    assert data["is_active"] is False

    # Verify that the email BackgroundTask was successfully called
    mock_send_email.assert_called_once()

async def test_registro_usuario_duplicado(client):
    """Test that the system rejects any registration attempts with already-registered email addresses (HTTP 400)."""
    # 1. Simulation of first-time user registration.
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    # 2. Attempt to register the same user with the same email again.
    response = await client.post("/usuarios/registro", json=USER_PAYLOAD)

    assert response.status_code == 400
    assert response.json()["detail"] == "Este usuario ya se encuentra registrado."


async def test_verificacion_email_exitosa(client, db_session):
    """Test that a valid JWT verification token activates the user."""
    # 1. Register user
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    # 2. Forge the verification token using the test secret key
    token = create_verification_token(USER_PAYLOAD["email"])

    # 3. Consume the verification endpoint
    response = await client.get(f"/usuarios/verificar-email?token={token}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # 4. Assert database state mutation
    stmt = select(User).where(User.email == USER_PAYLOAD["email"])
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    assert user.is_active is True

async def test_verificacion_email_token_invalido(client):
    """Test that invalid or corrupted tokens are rejected (HTTP 400)."""
    response = await client.get("/usuarios/verificar-email?token=tokenFalso123")
    assert response.status_code == 400
    assert "inválido" in response.json()["detail"].lower()

async def test_login_exitoso(client, db_session):
    """Test that a registered and active user can log in."""

    # 1. ARRANGE: User creation (backend will send it disabled by default is_active=False).
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    # 2. ARRANGE (State mutation): Simulation of successful user email verification.
    stmt = select(User).where(User.email == USER_PAYLOAD["email"])
    result = await db_session.execute(stmt)
    user = result.scalars().first()

    # Simulation of user activation at persistency layer.
    user.is_active = True
    await db_session.commit()

    # 3. ACT: Afterward, the verified user logs in.
    login_data = {
        "email": USER_PAYLOAD["email"],
        "password": USER_PAYLOAD["password"]
    }
    response = await client.post("/usuarios/login", json=login_data)

    # 4. ASSERT: After a successful login, response code should be 200 OK.
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_usuario_inactivo(client):
    """Test that registered but inactive users cannot log in (HTTP 403)."""
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    login_data = {
        "email": USER_PAYLOAD["email"],
        "password": USER_PAYLOAD["password"]
    }
    response = await client.post("/usuarios/login", json=login_data)

    assert response.status_code == 403
    assert "verificar su cuenta" in response.json()["detail"]

async def test_login_credenciales_invalidas(client):
    """Test that invalid credentials trigger an HTTP 401 response."""
    login_data = {
        "email": "noexiste@example.com",
        "password": "claveIncorrecta"
    }
    response = await client.post("/usuarios/login", json=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Revise su correo y contraseña"

async def test_borrado_logico_usuario(client, db_session):
    """Test that a soft-deleted user retains their DB row but cannot log in (HTTP 403)."""

    # 1. ARRANGE: Register and activate a user
    await client.post("/usuarios/registro", json=USER_PAYLOAD)
    stmt = select(User).where(User.email == USER_PAYLOAD["email"])
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    user.is_active = True
    await db_session.commit()

    # 2. ARRANGE: Login to get the Bearer token for authorization
    login_data = {"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]}
    login_response = await client.post("/usuarios/login", json=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. ACT: Request self-deletion using CEDULA instead of email
    target_cedula = USER_PAYLOAD["cedula"]
    target_email = USER_PAYLOAD["email"]
    delete_response = await client.delete(f"/usuarios/{target_cedula}", headers=headers)

    # 4. ASSERT: Verify successful response and exact custom message
    assert delete_response.status_code == 200
    response_data = delete_response.json()
    assert response_data["success"] is True
    assert response_data["message"] == f"La cuenta vinculada a {target_email}, con C.C. {target_cedula} ha sido eliminada exitosamente."

    # 5. ASSERT: Verify the row still exists but is structurally deactivated
    result = await db_session.execute(stmt)
    deleted_user = result.scalars().first()
    assert deleted_user is not None  # The row must NOT be deleted
    assert deleted_user.deleted_at is not None  # Timestamp must exist
    assert deleted_user.is_active is False  # Must be deactivated

    # 6. ASSERT: Attempt to login again should be strictly rejected
    failed_login = await client.post("/usuarios/login", json=login_data)
    assert failed_login.status_code == 401

# ==========================================
# RBAC AND USER MANAGEMENT (U+D) TESTS
# ==========================================

async def test_actualizacion_perfil_self_service_y_sanitizacion(client, db_session):
    """
    Validates that a standard tourist can securely update their own basic profile data.
    Strictly verifies that malicious attempts to escalate privileges (mutating 'role' or 'is_active')
    are sanitized and ignored by the Service Layer.
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

    # 2. ACT: Send PATCH request with valid and malicious fields
    update_payload = {
        "first_name": "Nombre Modificado", # Valid scalar update
        "role": "superadmin",              # Malicious escalation attempt
        "is_active": False                 # Malicious status mutation
    }
    response = await client.patch(f"/usuarios/{tourist.cedula}", json=update_payload, headers=headers)

    # 3. ASSERT: Response is successful and sanitization worked
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Nombre Modificado"
    assert data["role"] == "tourist"  # Must remain tourist
    assert data["is_active"] is True  # Must remain active

async def test_actualizacion_usuario_helpdesk_exitoso(client, db_session):
    """
    Validates the Helpdesk pattern: An Admin can update a Tourist's account.
    """
    # 1. ARRANGE: Create Admin
    admin = User(
        cedula="999999999", email="admin@asoprado.com", first_name="Admin", last_name="Test",
        password_hash=get_password_hash("pass"), role=UserRole.admin, is_active=True, data_consent=True
    )
    db_session.add(admin)

    # ARRANGE: Create Tourist
    tourist = User(
        cedula="111111111", email="turista2@asoprado.com", first_name="Juan", last_name="Test",
        password_hash=get_password_hash("pass"), role=UserRole.tourist, is_active=True, data_consent=True
    )
    db_session.add(tourist)
    await db_session.commit()

    admin_token = create_access_token(data={"sub": admin.email, "role": admin.role.value})

    # 2. ACT: Admin updates Tourist's email
    update_payload = {"email": "correo_corregido@asoprado.com"}
    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json=update_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
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
        cedula="888888888", email="admin2@asoprado.com", first_name="Admin", last_name="Test",
        password_hash=get_password_hash("pass"), role=UserRole.admin, is_active=True, data_consent=True
    )
    superadmin = User(
        cedula="000000000", email="super@asoprado.com", first_name="Super", last_name="Test",
        password_hash=get_password_hash("pass"), role=UserRole.superadmin, is_active=True, data_consent=True
    )
    db_session.add_all([admin, superadmin])
    await db_session.commit()

    admin_token = create_access_token(data={"sub": admin.email, "role": admin.role.value})

    # 2. ACT: Admin attempts to update Superadmin
    response = await client.patch(
        f"/usuarios/{superadmin.cedula}",
        json={"first_name": "Hacked"},
        headers={"Authorization": f"Bearer {admin_token}"}
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
    u1 = User(cedula="111111", email="t@t.com", first_name="Tania", last_name="Torres", password_hash="x", role=UserRole.tourist, is_active=True, data_consent=True)
    u2 = User(cedula="222222", email="a@a.com", first_name="Anastasia", last_name="Andrade", password_hash="x", role=UserRole.admin, is_active=True, data_consent=True)
    u3 = User(cedula="333333", email="s@s.com", first_name="Sofia", last_name="Sanchez", password_hash="x", role=UserRole.superadmin, is_active=True, data_consent=True)

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
    assert "superadmin" not in roles_returned # Obscured successfully