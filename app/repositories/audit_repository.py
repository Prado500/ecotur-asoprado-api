from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

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

    async def get_all_audit_logs(self, limit: int = 100) -> List[AuditLog]:
        """
        Retrieves the most recent audit logs, ordered by timestamp descending
        to surface the newest transactions first.
        """
        stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())