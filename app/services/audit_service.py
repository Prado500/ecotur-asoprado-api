from typing import Any

from app.models.audit import AuditAction, AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:
    """Encapsulates business logic, rules, and operational logic of the Audit Trail ecosystem."""

    def __init__(self, audit_repo: AuditRepository) -> None:
        self.audit_repo = audit_repo

    async def log_transaction(
        self,
        entity_name: str,
        entity_id: str,
        action: AuditAction,
        performed_by: str,
        changes: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Registers a structural or state mutation inside the system.

        This method is intended to be invoked internally by other domain services
        (e.g., UserService, TouristServicesService) whenever a write operation occurs.
        """
        new_log = AuditLog(
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            changes=changes,
            performed_by=performed_by,
        )
        return await self.audit_repo.create_audit_log(new_log)

    async def retrieve_audit_history(
        self,
        limit: int = 20,
        offset: int = 0,
        entity_name: str | None = None,
        entity_id: str | None = None,
    ) -> list[AuditLog]:
        """Retrieves one page of the global audit history, newest first.

        Who may read it is decided before this call, by the admin guard of the audit
        router (ADR-0012, point 1); the service applies no role rule of its own.

        Args:
            limit (int): Maximum number of records to return. Defaults to 20.
            offset (int): Number of records to skip for pagination.
            entity_name (str, optional): Filter by entity class name.
            entity_id (str, optional): Filter by exact entity identifier.

        Returns:
            List[AuditLog]: A collection of the requested audit logs.
        """
        return await self.audit_repo.get_all_audit_logs(
            limit=limit, offset=offset, entity_name=entity_name, entity_id=entity_id
        )
