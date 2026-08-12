from fastapi import HTTPException, status
from typing import List, Optional, Any

from app.repositories.audit_repository import AuditRepository
from app.models.audit import AuditLog, AuditAction
from app.models.user import User, UserRole

class AuditService:
    """
    Encapsulates business logic, rules, and operational logic of the Audit Trail ecosystem.
    """
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    async def log_transaction(
            self,
            entity_name: str,
            entity_id: str,
            action: AuditAction,
            performed_by: str,
            changes: Optional[dict[str, Any]] = None
    ) -> AuditLog:
        """
        Registers a structural or state mutation inside the system.

        This method is intended to be invoked internally by other domain services
        (e.g., UserService, TouristServicesService) whenever a write operation occurs.
        """
        new_log = AuditLog(
            entity_name=entity_name,
            entity_id=entity_id,
            action=action,
            changes=changes,
            performed_by=performed_by
        )
        return await self.audit_repo.create_audit_log(new_log)

    async def retrieve_audit_history(self, current_user: User, limit: int = 100) -> List[AuditLog]:
        """
        Retrieves the global audit history enforcing Role-Based Access Control.

        Strictly gated to Administrators and Superadmins.

        Args:
            current_user (User): The authenticated user making the request.
            limit (int): Maximum number of records to return. Defaults to 100.

        Returns:
            List[AuditLog]: A collection of the most recent audit logs.

        Raises:
            HTTPException: 403 Forbidden if the requester is a standard tourist.
        """
        if current_user.role not in [UserRole.admin, UserRole.superadmin]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios insuficientes para visualizar la auditoría del sistema."
            )

        return await self.audit_repo.get_all_audit_logs(limit=limit)