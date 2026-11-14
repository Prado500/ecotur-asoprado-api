"""Creation of the first superadmin of an empty platform (BE-34, ADR-0015).

No HTTP route can create the first superadmin: provisioning and role changes already require
one. This service is called by the bootstrap command (app/cli/bootstrap_superadmin.py), run by
an operator, never by the web app.
"""

from app.core.exceptions import AlreadyExistsError
from app.core.security import get_password_hash
from app.models.audit import AuditAction
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateByAdmin
from app.services.audit_service import AuditService


async def bootstrap_superadmin(
    credentials: UserCreateByAdmin,
    user_repo: UserRepository,
    audit_service: AuditService,
) -> User | None:
    """Creates an active superadmin when none can sign in; otherwise writes nothing.

    Idempotent: while an active, non-deleted superadmin exists, every call returns None. The
    account is always an active superadmin, whatever role or is_active the credentials carry.
    It never promotes, reactivates or recovers an existing account: a cedula or email already
    in any row (any role, active, inactive or deleted) stops it, so it is no escalation path.
    There is no authenticated actor, so the new superadmin is recorded as the author of its
    own creation, as a tourist is in register_tourist.

    Args:
        credentials (UserCreateByAdmin): Account data, already validated by the account rules.
        user_repo (UserRepository): Data access for users.
        audit_service (AuditService): Records the creation.

    Returns:
        User | None: The new superadmin, or None when an active one already exists.

    Raises:
        AlreadyExistsError: When the cedula or email already belongs to an account.
    """
    if await user_repo.count_active_superadmins() > 0:
        return None

    existing_user = await user_repo.get_user_by_email_or_cedula(
        email=credentials.email, cedula=credentials.cedula
    )
    if existing_user:
        raise AlreadyExistsError(
            "La cédula o el correo del superadministrador ya pertenecen a una cuenta."
        )

    new_user = User(
        cedula=credentials.cedula,
        email=credentials.email,
        first_name=credentials.first_name,
        last_name=credentials.last_name,
        phone=credentials.phone,
        password_hash=get_password_hash(credentials.password),
        role=UserRole.superadmin,
        data_consent=True,
        is_active=True,
    )
    saved_user = await user_repo.create_user(new_user)

    await audit_service.log_transaction(
        entity_name="User",
        entity_id=saved_user.cedula,
        action=AuditAction.CREATE,
        performed_by=saved_user.cedula,
        changes={"role": UserRole.superadmin.value, "source": "bootstrap"},
    )

    return saved_user
