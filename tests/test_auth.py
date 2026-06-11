import pytest

USER_PAYLOAD = {
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
    assert "password" not in data # Garantiza que no exponemos la contraseña plana

async def test_registro_usuario_duplicado(client):
    """Prueba que el sistema rechace un registro con un correo ya existente (HTTP 400)."""
    # 1. Registramos al usuario por primera vez
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    # 2. Intentamos registrar el mismo usuario nuevamente
    response = await client.post("/usuarios/registro", json=USER_PAYLOAD)

    assert response.status_code == 400
    assert response.json()["detail"] == "Este correo electrónico ya se encuentra registrado."

async def test_login_exitoso(client):
    """Prueba que un usuario registrado pueda iniciar sesión y recibir un JWT."""
    # 1. Crear el usuario
    await client.post("/usuarios/registro", json=USER_PAYLOAD)

    # 2. Iniciar sesión
    login_data = {
        "email": USER_PAYLOAD["email"],
        "password": USER_PAYLOAD["password"]
    }
    response = await client.post("/usuarios/login", json=login_data)

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