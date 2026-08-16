from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.models.audit import AuditLog

class AuditRepository:
    """
    Handles data access (SQL transactions) regarding the AuditLog entity.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_audit_log(self, audit_log: AuditLog) -> AuditLog:
        """
        Persists a new audit trail record into the database.
        """
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log

async def get_all_audit_logs(
        self,
        limit: int = 20,
        offset: int = 0,
        entity_name: Optional[str] = None,
        entity_id: Optional[str] = None
) -> List[AuditLog]:
    """
    Retrieves the audit logs utilizing explicit pagination (limit/offset)
    and optional dynamic equality filters to prevent Over-fetching.
    """
    stmt = select(AuditLog)

    # Dynamic SQL Query Building based on provided filters
    if entity_name:
        stmt = stmt.where(AuditLog.entity_name == entity_name)
    if entity_id:
        stmt = stmt.where(AuditLog.entity_id == entity_id)

    # Apply ordering and Pagination
    stmt = stmt.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset)

    result = await self.db.execute(stmt)
    return list(result.scalars().all())