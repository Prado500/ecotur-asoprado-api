"""ORM models package: importing it registers every table on ``Base.metadata``.

Alembic's ``env.py`` imports this package for autogenerate, so a new model module must be
imported here and listed in ``__all__``; otherwise autogenerate does not see its table.
"""

from app.models.audit import AuditLog
from app.models.service import ServiceImage, TouristService
from app.models.user import User

__all__ = ["AuditLog", "ServiceImage", "TouristService", "User"]
