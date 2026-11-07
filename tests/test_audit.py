from typing import Any
from unittest.mock import create_autospec

import pytest

from app.core.exceptions import AuthorizationError
from app.models.audit import AuditAction, AuditLog
from app.models.user import UserRole
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService
from app.services.user_access_policy import UserAccessPolicy


async def test_audit_trail_creation_and_retrieval(client, persist_user, make_auth_headers):
    """
    Validates that operations across the system successfully emit silent snapshots
    to the Audit Trail via Dependency Injection.
    """
    superadmin = await persist_user(role=UserRole.superadmin)
    headers = make_auth_headers(superadmin)

    # 1. Sustituimos el multipart/form-data por un JSON puro que cumple con ServiceCreate
    json_payload = {
        "name": "Paquete De Auditoria Test",
        "category": "otro",
        "description": "Prueba con JSON puro sin multipart",
        "base_price": 50000,
        "max_capacity": 10,
        "is_available": True,
        "image_urls": [
            "https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/test.jpg"
        ],
    }

    post_response = await client.post("/servicios/", json=json_payload, headers=headers)

    assert post_response.status_code == 201

    # 2. Retrieve Audit History
    response = await client.get("/auditoria/", headers=headers)

    assert response.status_code == 200
    logs = response.json()

    assert len(logs) > 0
    assert logs[0]["entity_name"] == "TouristService"
    assert logs[0]["action"] == "CREATE"


async def test_audit_trail_forbidden_for_tourist(client, persist_user, make_auth_headers):
    """
    Validates RBAC restrictions ensuring tourists cannot read sensitive system logs.
    """
    tourist = await persist_user(role=UserRole.tourist)

    response = await client.get("/auditoria/", headers=make_auth_headers(tourist))

    assert response.status_code == 403
    assert isinstance(response.json()["detail"], str)


# ==========================================
# UNIT TESTS (pure service delegation contract)
# ==========================================


class TestAuditServiceAuthorization:
    """Freezes the service-level authorization delegation to UserAccessPolicy."""

    @pytest.fixture
    def audit_repo(self) -> Any:
        """Provides a strict autospec'd AuditRepository so signature drift fails tests."""
        return create_autospec(AuditRepository, instance=True)

    def _make_service(self, audit_repo) -> AuditService:
        return AuditService(audit_repo=audit_repo, user_access_policy=UserAccessPolicy())

    async def test_tourist_raises_authorization_error_and_repo_never_called(
        self, audit_repo, make_user
    ):
        tourist = make_user(role=UserRole.tourist)
        service = self._make_service(audit_repo)

        with pytest.raises(AuthorizationError):
            await service.retrieve_audit_history(current_user=tourist)

        audit_repo.get_all_audit_logs.assert_not_called()
        audit_repo.get_all_audit_logs.assert_not_awaited()

    async def test_admin_calls_repo_exactly_once_with_expected_args(self, audit_repo, make_user):
        admin = make_user(role=UserRole.admin)
        expected_logs = [
            AuditLog(entity_name="User", entity_id="1", action=AuditAction.CREATE, performed_by="1")
        ]
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


async def test_audit_trail_accessible_for_admin(
    client, db_session, persist_user, make_auth_headers
):
    """Admin role passes the router gate and receives the serialized log collection."""
    admin = await persist_user(role=UserRole.admin)
    await AuditRepository(db_session).create_audit_log(
        AuditLog(
            entity_name="User", entity_id="1", action=AuditAction.CREATE, performed_by=admin.cedula
        )
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
