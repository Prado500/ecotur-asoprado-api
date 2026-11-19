from collections.abc import Mapping
from typing import Any

from pydantic import TypeAdapter

from app.models.audit import AuditAction, AuditLog
from app.repositories.audit_repository import AuditRepository

# Dumps any column or validated value to its JSON form: Decimal and enum members become text.
_JSON_VALUE: TypeAdapter[Any] = TypeAdapter(Any)


def audit_value(value: Any) -> Any:
    """Returns a value in the JSON form an audit row stores.

    Decimal and enum members become text, as model_dump(mode="json") wrote them before
    (ADR-0021).

    Args:
        value: A stored column value or a validated field value.

    Returns:
        The same value, ready for the JSON column of the audit row.
    """
    return _JSON_VALUE.dump_python(value, mode="json")


def changed_fields(entity: object, new_values: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Returns the fields whose validated value differs from the stored one, as old and new.

    Compares Python values, not their text: Decimal("50000") equals the stored
    Decimal("50000.00"), and a value the schema normalizes to what is stored is no change
    (ADR-0021). Runs after the access policy, which decides on the keys sent, and before
    any setattr, which would overwrite the old value.

    Args:
        entity: The ORM row as it is stored.
        new_values: The validated values sent, keyed by attribute name.

    Returns:
        {field: {"old": ..., "new": ...}} in JSON form for each field that changes; empty
        when nothing does.
    """
    return {
        field: {"old": audit_value(getattr(entity, field)), "new": audit_value(value)}
        for field, value in new_values.items()
        if getattr(entity, field) != value
    }


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
