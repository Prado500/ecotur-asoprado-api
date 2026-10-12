from typing import List, Optional, Any

from app.repositories.audit_repository import AuditRepository
from app.models.audit import AuditLog, AuditAction
from app.models.user import User
from app.services.user_access_policy import UserAccessPolicy

class AuditService:
    """
    Encapsulates business logic, rules, and operational logic of the Audit Trail ecosystem.
    """
    def __init__(self, audit_repo: AuditRepository, user_access_policy: UserAccessPolicy):
        self.audit_repo = audit_repo
        self.user_access_policy = user_access_policy

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

    async def retrieve_audit_history(
            self,
            current_user: User,
            limit: int = 20,
            offset: int = 0,
            entity_name: Optional[str] = None,
            entity_id: Optional[str] = None
    ) -> List[AuditLog]:
        """
        Retrieves the global audit history enforcing Role-Based Access Control.

        Authorization is delegated to the UserAccessPolicy administrative-tier
        rule, keeping the service free of role comparisons and transport
        semantics. Strictly gated to Administrators and Superadmins.

        Args:
            current_user (User): The authenticated user making the request.
            limit (int): Maximum number of records to return. Defaults to 20.
            offset (int): Number of records to skip for pagination.
            entity_name (str, optional): Filter by entity class name.
            entity_id (str, optional): Filter by exact entity identifier.

        Returns:
            List[AuditLog]: A collection of the requested audit logs.

        Raises:
            AuthorizationError: If the requester is a standard tourist.
        """
        self.user_access_policy.assert_is_admin_plus(current_user)

        return await self.audit_repo.get_all_audit_logs(
            limit=limit,
            offset=offset,
            entity_name=entity_name,
            entity_id=entity_id
        )
