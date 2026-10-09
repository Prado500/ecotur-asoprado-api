import os
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.api.dependencies import get_current_admin_user, get_current_user, get_user_service
from app.models.user import User
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserCreateByAdmin, UserLogin, UserResponse, UserUpdate
from app.services.user_service import UserService

# -------------------------------------------------------------------
# DEPENDENCY TYPE ALIASES (PEP 593)
# Reusable injection contracts that remove the repetitive manual
# "usuario_actual: User = Depends(...)" boilerplate from every
# endpoint signature.
# -------------------------------------------------------------------

UserDep = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, Depends(get_current_admin_user)]

# -------------------------------------------------------------------
# ROUTER SEGMENTATION (RBAC at the transport boundary)
# Authorization is centralized in the router layer:
#   - public_router: no auth dependency (registration, login, verification).
#   - self_service_router: requires an authenticated session; handlers inject
#     the user only when the service needs the identity (audit, ABAC).
#   - admin_router: requires admin/superadmin privileges; handlers inject the
#     user only when the service needs the identity.
# Services keep pure business rules (hierarchical ABAC, data scoping) and
# never duplicate the transport-level authorization frontier.
# -------------------------------------------------------------------

public_router = APIRouter()
self_service_router = APIRouter(dependencies=[Depends(get_current_user)])
admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])


# -------------------------------------------------------------------
# PUBLIC ENDPOINTS
# -------------------------------------------------------------------

@public_router.post("/registro", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registrar_turista(
        usuario: UserCreate,
        background_tasks: BackgroundTasks,
        user_service: UserService = Depends(get_user_service)
):
    """
    Public endpoint: Registers a new tourist account.

    Delegates the registration pipeline to UserService and dispatches the
    account-verification email as a background task to avoid blocking the
    HTTP response.

    Args:
        usuario (UserCreate): Validated payload describing the new tourist account.
        background_tasks (BackgroundTasks): Starlette task queue for email dispatch.
        user_service (UserService): Injected business-logic service.

    Returns:
        UserResponse: JSON representation of the newly persisted inactive user.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")

    return await user_service.register_tourist(
        user_data=usuario,
        background_tasks=background_tasks,
        base_url=frontend_url
    )


@public_router.get("/verificar-email", status_code=status.HTTP_200_OK)
async def verificar_cuenta(
        token: str,
        user_service: UserService = Depends(get_user_service)
):
    """
    Public endpoint: Activates a user account via the emailed verification token.

    Args:
        token (str): Single-use JWT issued during registration.
        user_service (UserService): Injected business-logic service.

    Returns:
        dict: JSON payload confirming successful account activation.
    """
    return await user_service.verify_email_account(token)


@public_router.post("/login", response_model=TokenResponse)
async def login(
        credenciales: UserLogin,
        user_service: UserService = Depends(get_user_service)
):
    """
    Public endpoint: Authenticates credentials and issues an access JWT.

    Args:
        credenciales (UserLogin): Validated credentials payload (email + password).
        user_service (UserService): Injected business-logic service.

    Returns:
        TokenResponse: Signed bearer token granting access to protected resources.
    """
    return await user_service.authenticate_user(credenciales)


# -------------------------------------------------------------------
# SELF-SERVICE ENDPOINTS (any authenticated user)
# -------------------------------------------------------------------

@self_service_router.get("/mi-perfil", response_model=UserResponse)
async def ver_mi_perfil(usuario_actual: UserDep):
    """
    Protected endpoint: Returns the authenticated user's own profile.

    Args:
        usuario_actual (User): User extracted from the active JWT session.

    Returns:
        UserResponse: JSON representation of the requesting user's generic data.
    """
    return usuario_actual


@self_service_router.delete("/{cedula}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(
        cedula: str,
        usuario_actual: UserDep,
        user_service: UserService = Depends(get_user_service)
):
    """
    Protected endpoint: Performs a soft-delete on a target user account.

    Hierarchical ABAC is delegated to UserService: the action is allowed only
    on self-deletion or when the actor's role strictly outranks the target's.

    Args:
        cedula (str): Primary identifier of the account to soft-delete.
        usuario_actual (User): Authenticated user executing the operation.
        user_service (UserService): Injected business-logic service.

    Returns:
        dict: Standardized JSON confirmation payload.
    """
    return await user_service.delete_user_account(
        target_cedula=cedula,
        current_user=usuario_actual
    )


@self_service_router.patch("/{cedula}", response_model=UserResponse)
async def actualizar_usuario(
        cedula: str,
        update_data: UserUpdate,
        usuario_actual: UserDep,
        user_service: UserService = Depends(get_user_service)
):
    """
    Protected endpoint: Updates a specific user's profile information.

    Tourist users may self-update certain fields. Strict RBAC precedence and
    self-service rules are delegated to UserService.

    Args:
        cedula (str): Primary identifier of the account to update.
        update_data (UserUpdate): Partial JSON payload (PATCH behavior).
        usuario_actual (User): Authenticated user executing the update.
        user_service (UserService): Injected business-logic service.

    Returns:
        UserResponse: JSON representation of the refreshed user.
    """
    return await user_service.update_user_account(
        target_cedula=cedula,
        update_data=update_data,
        current_user=usuario_actual
    )


# -------------------------------------------------------------------
# ADMIN ENDPOINTS (admin + superadmin)
# -------------------------------------------------------------------

@admin_router.get("/", response_model=list[UserResponse])
async def listar_usuarios(
        usuario_actual: AdminDep,
        user_service: UserService = Depends(get_user_service)
):
    """
    Protected endpoint: Retrieves the user directory.

    Delegates hierarchical visibility rules to UserService so standard admins
    cannot retrieve superadmin entities.

    Args:
        usuario_actual (User): Authenticated administrator executing the query.
        user_service (UserService): Injected business-logic service.

    Returns:
        list[UserResponse]: Scoped JSON list of the registered user directory.
    """
    return await user_service.get_all_registered_users(usuario_actual)


@admin_router.get("/admin/eliminados", response_model=list[UserResponse])
async def listar_usuarios_eliminados(
        usuario_actual: AdminDep,
        user_service: UserService = Depends(get_user_service)
):
    """
    Protected endpoint: Retrieves the collection of logically deleted users.

    Delegates hierarchical visibility rules to UserService so standard admins
    cannot retrieve soft-deleted superadmin entities.

    Args:
        usuario_actual (User): Authenticated administrator executing the query.
        user_service (UserService): Injected business-logic service.

    Returns:
        list[UserResponse]: Scoped JSON list of the recycle-bin directory.
    """
    return await user_service.get_deleted_users(usuario_actual)


@admin_router.patch("/{cedula}/recuperar")
async def recuperar_usuario(
        cedula: str,
        usuario_actual: AdminDep,
        user_service: UserService = Depends(get_user_service)
):
    """
    Protected endpoint: Recovers a soft-deleted user account.

    Delegates RBAC precedence rules to UserService to prevent standard admins
    from recovering equal or higher-tier accounts.

    Args:
        cedula (str): Primary identifier of the account to recover.
        usuario_actual (User): Authenticated administrator executing the operation.
        user_service (UserService): Injected business-logic service.

    Returns:
        dict: Standardized JSON confirmation payload.
    """
    return await user_service.recover_user_account(
        target_cedula=cedula,
        current_user=usuario_actual
    )


@admin_router.post("/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def crear_administrador(
        usuario: UserCreateByAdmin,
        usuario_actual: AdminDep,
        user_service: UserService = Depends(get_user_service)
):
    """
    Protected endpoint: Provisions a new administrative account.

    The admin-tier dependency gates transport access, while UserService
    enforces the stricter superadmin-only hierarchical rule.

    Args:
        usuario (UserCreateByAdmin): Validated DTO with explicit role definition.
        usuario_actual (User): Authenticated administrator executing the operation.
        user_service (UserService): Injected business-logic service.

    Returns:
        UserResponse: JSON representation of the newly provisioned account.
    """
    return await user_service.create_administrative_account(
        user_data=usuario,
        current_user=usuario_actual
    )


router = APIRouter()
router.include_router(public_router)
router.include_router(self_service_router)
router.include_router(admin_router)
