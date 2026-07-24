from unittest.mock import patch

import pytest
from sqlalchemy.future import select

from app.core.security import create_verification_token
from app.models.user import User

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