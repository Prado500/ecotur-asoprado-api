from typing import Any
from unittest.mock import create_autospec

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models.audit import AuditAction, AuditLog
from app.models.user import UserRole
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService


async def test_audit_trail_creation_and_retrieval(client, persist_user, make_auth_headers):
    """
    Validates that operations across the system successfully emit silent snapshots
    to the Audit Trail via Dependency Injection.
    """
    superadmin = await persist_user(role=UserRole.superadmin)
    headers = make_auth_headers(superadmin)

    # 1. Create a package with a plain JSON payload that satisfies ServiceCreate
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


# ==========================================
# UNIT TESTS (pure service delegation contract)
# ==========================================


class TestAuditServiceHistory:
    """Freezes the history read: a pure delegation to the repository, with no role rule."""

    @pytest.fixture
    def audit_repo(self) -> Any:
        """Provides a strict autospec'd AuditRepository so signature drift fails tests."""
        return create_autospec(AuditRepository, instance=True)

    async def test_forwards_page_and_filters_to_repository_once(self, audit_repo):
        expected_logs = [
            AuditLog(entity_name="User", entity_id="1", action=AuditAction.CREATE, performed_by="1")
        ]
        audit_repo.get_all_audit_logs.return_value = expected_logs
        service = AuditService(audit_repo)

        result = await service.retrieve_audit_history(
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

    async def test_uses_first_page_of_twenty_without_filters_by_default(self, audit_repo):
        audit_repo.get_all_audit_logs.return_value = []
        service = AuditService(audit_repo)

        await service.retrieve_audit_history()

        audit_repo.get_all_audit_logs.assert_called_once_with(
            limit=20, offset=0, entity_name=None, entity_id=None
        )

    async def test_returns_empty_list_when_repository_has_no_rows(self, audit_repo):
        audit_repo.get_all_audit_logs.return_value = []
        service = AuditService(audit_repo)

        result = await service.retrieve_audit_history(entity_name="Ghost")

        assert result == []
        audit_repo.get_all_audit_logs.assert_called_once_with(
            limit=20, offset=0, entity_name="Ghost", entity_id=None
        )

    async def test_propagates_repository_failure(self, audit_repo):
        audit_repo.get_all_audit_logs.side_effect = SQLAlchemyError("database unavailable")
        service = AuditService(audit_repo)

        with pytest.raises(SQLAlchemyError):
            await service.retrieve_audit_history()

        audit_repo.get_all_audit_logs.assert_called_once_with(
            limit=20, offset=0, entity_name=None, entity_id=None
        )


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


async def test_audit_history_filters_by_entity_name_and_id(
    client, db_session, persist_user, make_auth_headers
):
    """Both query filters reach the query: only the log matching name and id comes back."""
    admin = await persist_user(role=UserRole.admin)
    audit_repo = AuditRepository(db_session)
    for entity_name, entity_id in (("User", "1"), ("User", "2"), ("TouristService", "2")):
        await audit_repo.create_audit_log(
            AuditLog(
                entity_name=entity_name,
                entity_id=entity_id,
                action=AuditAction.CREATE,
                performed_by=admin.cedula,
            )
        )

    response = await client.get(
        "/auditoria/",
        params={"entity_name": "User", "entity_id": "2"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["entity_name"] == "User"
    assert logs[0]["entity_id"] == "2"
