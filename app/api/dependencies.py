from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.storage import AzureStorageClient
from app.db.database import get_db
from app.models.user import User, UserRole
from app.repositories.audit_repository import AuditRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenData
from app.services.audit_service import AuditService
from app.services.tourist_services_service import TouristServicesService
from app.services.user_access_policy import UserAccessPolicy
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

# --- DEPENDENCY FACTORY (Inversion of Control) ---


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_tourist_services_repository(db: AsyncSession = Depends(get_db)) -> ServiceRepository:
    return ServiceRepository(db)


def get_audit_repository(db: AsyncSession = Depends(get_db)) -> AuditRepository:
    return AuditRepository(db)


def get_user_access_policy() -> UserAccessPolicy:
    return UserAccessPolicy()


def get_audit_service(
    audit_repo: AuditRepository = Depends(get_audit_repository),
    user_access_policy: UserAccessPolicy = Depends(get_user_access_policy),
) -> AuditService:
    return AuditService(audit_repo, user_access_policy)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    audit_service: AuditService = Depends(get_audit_service),
    user_access_policy: UserAccessPolicy = Depends(get_user_access_policy),
) -> UserService:
    return UserService(user_repo, audit_service, user_access_policy)


# --- AZURE BLOB STORAGE DEPENDENCY HANDLING --- #


def get_storage_client(settings: Settings = Depends(get_settings)) -> AzureStorageClient:
    """Builds the Azure Blob Storage adapter from the injected settings.

    The adapter reads no configuration of its own (ADR-0013): the connection string and both
    container names come from Settings, so overriding get_settings changes them.

    Args:
        settings (Settings): Application settings; supplies the connection string and the
            permanent and temporal container names.

    Returns:
        AzureStorageClient: Adapter bound to the configured account and containers.
    """
    return AzureStorageClient(
        connection_string=settings.azure_storage_connection_string,
        container_name=settings.azure_container_name,
        temporal_container_name=settings.azure_temporal_container_name,
    )


def get_service_service(
    service_repo: ServiceRepository = Depends(get_tourist_services_repository),
    audit_service: AuditService = Depends(get_audit_service),
    storage_client: AzureStorageClient = Depends(get_storage_client),
) -> TouristServicesService:
    return TouristServicesService(service_repo, audit_service, storage_client)


# --- ENDPOINT ACCESS CONTROL ---


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> User:
    """Decodes the given JWT token and resolves the active user it identifies.

    Verifies signature, payload consistency, lifespan status (unexpired or expired) and user
    enabling (only active users are allowed). The signature is checked with the injected
    settings, so a test or a key rotation that overrides get_settings is honoured.

    Args:
        token (str): Bearer token extracted by the OAuth2 scheme.
        user_repo (UserRepository): Repository used to consult the user state.
        settings (Settings): Application settings; supplies the JWT key and algorithm.

    Returns:
        User: The active, non-deleted user named by the token subject.

    Raises:
        HTTPException: 401 when the token is expired, corrupt, wrongly signed, has no
            subject, or names no active user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticidad de sus credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Su sesión ha expirado. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    except jwt.InvalidTokenError as err:
        raise credentials_exception from err

    # UserRepository is delegated to run the query
    user = await user_repo.get_non_deleted_user_by_email(token_data.email)

    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Validates if the provided user possesses administrative privileges.

    This method acts as a Role-Based Access Control (RBAC) gatekeeper
    to prevent unauthorized access to resources that should only be available for admin or
    superadmin users.

    Args:
    current_user (User): The user entity extracted from the current JWT session.

    Raises:
    HTTPException: 403 Forbidden if the user's role is not 'admin' or 'superadmin' .
    """
    if current_user.role not in [UserRole.admin, UserRole.superadmin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Privilegios insuficientes."
        )
    return current_user


# --- IDENTITY ALIASES (ADR-0012, point 5) ---
# The single way a handler receives the caller under a guard: the alias names the guard, so
# the signature says with which right the route acts.

UserDep = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, Depends(get_current_admin_user)]
