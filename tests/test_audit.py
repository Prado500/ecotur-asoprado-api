from unittest.mock import patch, create_autospec

import pytest
from app.models.user import User, UserRole
from sqlalchemy.future import select
from app.core.security import get_password_hash, create_access_token
from app.core.exceptions import AuthorizationError
from app.models.audit import AuditLog, AuditAction
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService
from app.services.user_access_policy import UserAccessPolicy

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


# ==========================================
# UNIT TESTS (pure service delegation contract)
# ==========================================


class TestAuditServiceAuthorization:
    """Freezes the service-level authorization delegation to UserAccessPolicy."""

    @pytest.fixture
    def audit_repo(self) -> AuditRepository:
        """Provides a strict autospec'd AuditRepository so signature drift fails tests."""
        return create_autospec(AuditRepository, instance=True)

    def _make_service(self, audit_repo) -> AuditService:
        return AuditService(audit_repo=audit_repo, user_access_policy=UserAccessPolicy())

    async def test_tourist_raises_authorization_error_and_repo_never_called(self, audit_repo, make_user):
        tourist = make_user(role=UserRole.tourist)
        service = self._make_service(audit_repo)

        with pytest.raises(AuthorizationError):
            await service.retrieve_audit_history(current_user=tourist)

        audit_repo.get_all_audit_logs.assert_not_called()
        audit_repo.get_all_audit_logs.assert_not_awaited()

    async def test_admin_calls_repo_exactly_once_with_expected_args(self, audit_repo, make_user):
        admin = make_user(role=UserRole.admin)
        expected_logs = [AuditLog(entity_name="User", entity_id="1", action=AuditAction.CREATE, performed_by="1")]
        audit_repo.get_all_audit_logs.return_value = expected_logs
        service = self._make_service(audit_repo)

        result = await service.retrieve_audit_history(
            current_user=admin,
            limit=5,
            offset=10,
            entity_name="User",
            entity_id="1",
        )

        audit_repo.get_all_audit_logs.assert_called_once_with(
            limit=5,
            offset=10,
            entity_name="User",
            entity_id="1",
        )
        assert result == expected_logs


# ==========================================
# INTEGRATION TESTS (router-level gate)
# ==========================================


async def test_audit_trail_accessible_for_admin(client, db_session, persist_user, make_auth_headers):
    """Admin role passes the router gate and receives the serialized log collection."""
    admin = await persist_user(role=UserRole.admin)
    await AuditRepository(db_session).create_audit_log(
        AuditLog(entity_name="User", entity_id="1", action=AuditAction.CREATE, performed_by=admin.cedula)
    )

    response = await client.get("/auditoria/", headers=make_auth_headers(admin))

    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["entity_name"] == "User"
    assert logs[0]["entity_id"] == "1"
    assert logs[0]["action"] == "CREATE"


async def test_audit_trail_requires_authentication(client):
    """Missing bearer token is rejected by the router gate with a 401 detail body."""
    response = await client.get("/auditoria/")

    assert response.status_code == 401
    assert "detail" in response.json()