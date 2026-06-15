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
    """Prueba que un usuario nuevo se pueda registrar correctamente."""
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
    """Prueba que el sistema rechace un registro con un correo ya existente (HTTP 400)."""
    # 1. Registramos al usuario por primera vez
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    # 2. Intentamos registrar el mismo usuario nuevamente
    response = await client.post("/usuarios/registro", json=USER_PAYLOAD)

    assert response.status_code == 400
    assert response.json()["detail"] == "Este usuario ya se encuentra registrado."

async def test_login_exitoso(client, db_session):
    """Prueba que un usuario registrado y ACTIVADO pueda iniciar sesión."""

    # 1. ARRANGE: Crear el usuario (El backend lo guarda como is_active=False)
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    # 2. ARRANGE (Mutación de Estado): Simulamos que ya hizo clic en el correo
    stmt = select(User).where(User.email == USER_PAYLOAD["email"])
    resultado = await db_session.execute(stmt)
    usuario = resultado.scalars().first()

    # Lo activamos manualmente a nivel de base de datos
    usuario.is_active = True
    await db_session.commit()

    # 3. ACT: Iniciar sesión (Solo enviamos lo que Pydantic exige)
    login_data = {
        "email": USER_PAYLOAD["email"],
        "password": USER_PAYLOAD["password"]
    }
    response = await client.post("/usuarios/login", json=login_data)

    # 4. ASSERT: Validamos que ahora sí entre con 200 OK
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_credenciales_invalidas(client):
    """Prueba que credenciales incorrectas devuelvan HTTP 401."""
    login_data = {
        "email": "noexiste@example.com",
        "password": "claveIncorrecta"
    }
    response = await client.post("/usuarios/login", json=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Revise su correo y contraseña"