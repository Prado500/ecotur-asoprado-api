import pytest
from sqlalchemy.future import select

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



async def test_registro_usuario_exitoso(client):
    """Test that a new user can successfully register."""
    response = await client.post("/usuarios/registro", json=USER_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["first_name"] == USER_PAYLOAD["first_name"]
    assert "id" in data
    assert "password" not in data
    assert data["cedula"] == USER_PAYLOAD["cedula"]
    assert data["is_active"] is False

async def test_registro_usuario_duplicado(client):
    """Test that the system rejects any registration attempts with already-registered email addresses (HTTP 400)."""
    # 1. Simulation of first-time user registration.
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    # 2. Attempt to register the same user with the same email again.
    response = await client.post("/usuarios/registro", json=USER_PAYLOAD)

    assert response.status_code == 400
    assert response.json()["detail"] == "Este usuario ya se encuentra registrado."

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

async def test_login_credenciales_invalidas(client):
    """Test that invalid credentials trigger an HTTP 401 response."""
    login_data = {
        "email": "noexiste@example.com",
        "password": "claveIncorrecta"
    }
    response = await client.post("/usuarios/login", json=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Revise su correo y contraseña"