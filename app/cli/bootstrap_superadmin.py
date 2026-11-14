"""Creates the first superadmin when no active one exists (BE-34, ADR-0015).

Run by an operator, once per environment, with the image the CD deploys, as the CD runs the
migrations; never at startup, never over HTTP:

    docker run --rm -e DATABASE_URL=... -e SUPERADMIN_CEDULA=... -e SUPERADMIN_EMAIL=...
        -e SUPERADMIN_FIRST_NAME=... -e SUPERADMIN_LAST_NAME=... -e SUPERADMIN_PASSWORD=...
        <image> python -m app.cli.bootstrap_superadmin

Locally: ./venv/Scripts/python.exe -m app.cli.bootstrap_superadmin, with the six variables in
.env or in the environment. Exit code 0: created, or an active superadmin already exists (nothing
written). Exit code 1: a variable is missing or breaks the account rules, or the cedula or email
already belongs to an account (nothing written). The password is never printed.
"""

import asyncio
import sys

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import SuperadminBootstrapSettings
from app.core.exceptions import AlreadyExistsError
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateByAdmin, UserRole
from app.services.audit_service import AuditService
from app.services.superadmin_bootstrap import bootstrap_superadmin


async def _bootstrap(database_url: str, credentials: UserCreateByAdmin) -> User | None:
    """Runs the bootstrap in one session over an engine of its own, disposed at the end.

    The engine is not the web app's (app/db/database.py, echo=True): with echo off, the INSERT
    parameters (email, cedula, password hash) are not written to the output.

    Args:
        database_url (str): SQLAlchemy async URL of the target database.
        credentials (UserCreateByAdmin): Validated account data.

    Returns:
        User | None: The new superadmin, or None when an active one already exists.

    Raises:
        AlreadyExistsError: When the cedula or email already belongs to an account.
    """
    engine = create_async_engine(database_url)
    try:
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory() as session:
            return await bootstrap_superadmin(
                credentials,
                UserRepository(session),
                AuditService(AuditRepository(session)),
            )
    finally:
        await engine.dispose()


def _report(error: ValidationError) -> None:
    """Prints each failing variable and its error type to stderr, never its value.

    Args:
        error (ValidationError): From SuperadminBootstrapSettings or UserCreateByAdmin; an
            account field (password, cedula...) is reported by its variable name.
    """
    for detail in error.errors(include_input=False, include_url=False):
        field = str(detail["loc"][0])
        if field not in SuperadminBootstrapSettings.model_fields:
            field = f"superadmin_{field}"
        print(f"{field.upper()}: {detail['type']}", file=sys.stderr)


def main() -> int:
    """Reads and validates the credentials, then creates the superadmin if none is active.

    Returns:
        int: The exit code: 0 created or already present; 1 on error, with nothing written.
    """
    try:
        settings = SuperadminBootstrapSettings()
        credentials = UserCreateByAdmin(
            cedula=settings.superadmin_cedula,
            email=settings.superadmin_email,
            first_name=settings.superadmin_first_name,
            last_name=settings.superadmin_last_name,
            password=settings.superadmin_password.get_secret_value(),
            data_consent=True,
            role=UserRole.superadmin,
            is_active=True,
        )
    except ValidationError as error:
        _report(error)
        return 1

    try:
        created = asyncio.run(_bootstrap(settings.database_url, credentials))
    except AlreadyExistsError:
        print(
            "SUPERADMIN_CEDULA o SUPERADMIN_EMAIL ya pertenecen a una cuenta; no se escribió nada.",
            file=sys.stderr,
        )
        return 1

    if created is None:
        print("Ya existe un superadministrador activo; no se escribió nada.")
    else:
        print(f"Superadministrador creado: {created.email}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
