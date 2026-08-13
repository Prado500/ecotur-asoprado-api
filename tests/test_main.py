import pytest

async def test_read_root(client):
    """
    verifies the root health check endpoint responds with an 200 code and the defined response message.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "El ASOPRADO API (v0.2.0-dev) está en línea"}