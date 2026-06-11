import pytest

async def test_read_root(client):
    """
    Verifica que el endpoint raíz responda 200 OK y devuelva el mensaje esperado.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Ecotur-ASOPRADO API (Iteración 1) está en línea"}