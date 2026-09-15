from unittest.mock import patch

import pytest
from app.models.user import User, UserRole
from sqlalchemy.future import select
from app.core.security import get_password_hash, create_access_token
from app.models.audit import AuditLog

@pytest.fixture
async def superadmin_token(db_session) -> dict:
    admin = User(
        cedula="999888", email="audit@test.com", first_name="AdminAdmin", last_name="AdminAdmin",
        password_hash=get_password_hash("ciscociscoA1"), role=UserRole.superadmin,
        is_active=True, data_consent=True
    )
    db_session.add(admin)
    await db_session.commit()
    token = create_access_token(data={"sub": admin.email, "role": admin.role.value})
    return {"Authorization": f"Bearer {token}"}

async def test_audit_trail_creation_and_retrieval(client, superadmin_token, db_session):
    """
    Validates that operations across the system successfully emit silent snapshots
    to the Audit Trail via Dependency Injection.
    """

    # 1. Sustituimos el multipart/form-data por un JSON puro que cumple con ServiceCreate
    json_payload = {
        "name": "Paquete De Auditoria Test",
        "category": "otro",
        "description": "Prueba con JSON puro sin multipart",
        "base_price": 50000,
        "max_capacity": 10,
        "is_available": True,
        "image_urls": ["https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/test.jpg"]
    }

    post_response = await client.post(
        "/servicios/",
        json=json_payload,
        headers=superadmin_token
    )

    assert post_response.status_code == 201

    # 2. Retrieve Audit History
    response = await client.get("/auditoria/", headers=superadmin_token)

    assert response.status_code == 200
    logs = response.json()

    assert len(logs) > 0
    assert logs[0]["entity_name"] == "TouristService"
    assert logs[0]["action"] == "CREATE"

async def test_audit_trail_forbidden_for_tourist(client, db_session):
    """
    Validates RBAC restrictions ensuring tourists cannot read sensitive system logs.
    """
    tourist = User(cedula="888", email="tourist@audit.com", first_name="T", last_name="T", password_hash="x", role=UserRole.tourist, is_active=True, data_consent=True)
    db_session.add(tourist)
    await db_session.commit()
    token = create_access_token(data={"sub": tourist.email, "role": tourist.role.value})

    response = await client.get("/auditoria/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403