from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.api.dependencies import (
    AdminDep,
    SuperadminDep,
    UserDep,
    get_current_admin_user,
    get_current_superadmin_user,
    get_current_user,
    get_user_service,
)
from app.core.config import Settings, get_settings
from app.core.email import send_verification_email
from app.schemas.message import MessageResponse
from app.schemas.token import TokenResponse
from app.schemas.user import (
    UserCreate,
    UserCreateByAdmin,
    UserLogin,
    UserResponse,
    UserUpdate,
    VerificationResendRequest,
)
from app.services.user_service import UserService

# -------------------------------------------------------------------
# ROUTER SEGMENTATION (RBAC at the transport boundary, ADR-0012)
# Each router's guard decides the role, once:
#   - public_router: no auth dependency (registration, login, verification).
#   - self_service_router: requires an authenticated session; handlers inject
#     the user only when the service needs the identity (audit, ABAC).
#   - admin_router: requires admin/superadmin privileges; handlers inject the
#     user only when the service needs the identity.
#   - superadmin_router: requires superadmin privileges (provisioning of
#     administrative accounts).
# Services keep the rules that depend on the data (hierarchical ABAC, data
# scoping) and never check the caller's role again.
# -------------------------------------------------------------------

public_router = APIRouter()

# The resend answers this whether or not a link left, so it never tells whether an account
# exists (BE-64, ADR-0023).
RESEND_VERIFICATION_MESSAGE = (
    "Si su correo tiene una cuenta pendiente de verificación, le acabamos de enviar un nuevo "
    "enlace. Revise su bandeja de entrada y la carpeta de correo no deseado. Si ya pidió uno "
    "hace poco, espere un minuto antes de intentarlo de nuevo."
)
self_service_router = APIRouter(dependencies=[Depends(get_current_user)])
admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])
superadmin_router = APIRouter(dependencies=[Depends(get_current_superadmin_user)])


# -------------------------------------------------------------------
# PUBLIC ENDPOINTS
# -------------------------------------------------------------------


@public_router.post("/registro", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registrar_turista(
    usuario: UserCreate,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
    settings: Settings = Depends(get_settings),
):
    """Public endpoint: Registers a new tourist account.

    Delegates the registration pipeline to UserService, which returns the
    persisted account plus its verification token. The activation email is
    scheduled here as a background task: the transport layer decides WHEN
    the email is dispatched, the service decides WHAT it carries.

    Args:
        usuario (UserCreate): Validated payload describing the new tourist account.
        background_tasks (BackgroundTasks): Starlette task queue for email dispatch.
        user_service (UserService): Injected business-logic service.
        settings (Settings): Injected configuration; frontend_url is the base of the emailed link.

    Returns:
        UserResponse: JSON representation of the newly persisted inactive user.
    """
    frontend_url = settings.frontend_url.rstrip("/")

    result = await user_service.register_tourist(user_data=usuario)

    background_tasks.add_task(
        send_verification_email,
        email_to=result.user.email,
        first_name=result.user.first_name,
        token=result.verification_token,
        base_url=frontend_url,
    )

    return result.user


@public_router.get("/verificar-email", status_code=status.HTTP_200_OK)
async def verificar_cuenta(token: str, user_service: UserService = Depends(get_user_service)):
    """Public endpoint: verifies the account's email with the emailed token.

    The first use fills the account's verification mark and activates the account if it
    is inactive; a later use changes nothing and answers with another message (ADR-0022).

    Args:
        token (str): Email-verification JWT issued during registration.
        user_service (UserService): Injected business-logic service.

    Returns:
        dict: Success flag and the message to show.
    """
    return await user_service.verify_email_account(token)


@public_router.post(
    "/reenviar-verificacion", response_model=MessageResponse, status_code=status.HTTP_200_OK
)
async def resend_verification_email(
    body: VerificationResendRequest,
    background_tasks: BackgroundTasks,
    user_service: UserService = Depends(get_user_service),
    settings: Settings = Depends(get_settings),
) -> dict[str, bool | str]:
    """Public endpoint: emails a new verification link to an account still waiting for one.

    The service decides whether a link is due (a non-deleted, unverified tourist past the
    resend interval) and signs it; the email leaves as a background task, as after a
    registration. The answer is the same in every case (ADR-0023); MessageResponse, the
    response_model, documents it and lets no other key out.

    Args:
        body (VerificationResendRequest): The address the link is asked for.
        background_tasks (BackgroundTasks): Starlette task queue for email dispatch.
        user_service (UserService): Injected business-logic service.
        settings (Settings): Injected configuration; frontend_url is the base of the emailed link.

    Returns:
        dict: Success flag and the message to show, identical whether or not a link left.
    """
    resend = await user_service.resend_verification_link(body.email)
    if resend is not None:
        background_tasks.add_task(
            send_verification_email,
            email_to=resend.user.email,
            first_name=resend.user.first_name,
            token=resend.verification_token,
            base_url=settings.frontend_url.rstrip("/"),
        )

    return {"success": True, "message": RESEND_VERIFICATION_MESSAGE}


@public_router.post("/login", response_model=TokenResponse)
async def login(credenciales: UserLogin, user_service: UserService = Depends(get_user_service)):
    """Public endpoint: Authenticates credentials and issues an access JWT.

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
    """Protected endpoint: Returns the authenticated user's own profile.

    Args:
        usuario_actual (User): User extracted from the active JWT session.

    Returns:
        UserResponse: JSON representation of the requesting user's generic data.
    """
    return usuario_actual


@self_service_router.delete("/{cedula}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(
    cedula: str, usuario_actual: UserDep, user_service: UserService = Depends(get_user_service)
):
    """Protected endpoint: Performs a soft-delete on a target user account.

    Hierarchical ABAC is delegated to UserService: the action is allowed only
    when the actor's role strictly outranks the target's, or on a tourist's
    own account; no other account deletes itself (ADR-0017, ADR-0019).

    Args:
        cedula (str): Primary identifier of the account to soft-delete.
        usuario_actual (User): Authenticated user executing the operation.
        user_service (UserService): Injected business-logic service.

    Returns:
        dict: Standardized JSON confirmation payload.
    """
    return await user_service.delete_user_account(target_cedula=cedula, current_user=usuario_actual)


@self_service_router.patch("/{cedula}", response_model=UserResponse)
async def actualizar_usuario(
    cedula: str,
    update_data: UserUpdate,
    usuario_actual: UserDep,
    user_service: UserService = Depends(get_user_service),
):
    """Protected endpoint: Updates a specific user's profile information.

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
        target_cedula=cedula, update_data=update_data, current_user=usuario_actual
    )


# -------------------------------------------------------------------
# ADMIN ENDPOINTS (admin + superadmin)
# -------------------------------------------------------------------


@admin_router.get("/", response_model=list[UserResponse])
async def listar_usuarios(
    usuario_actual: AdminDep, user_service: UserService = Depends(get_user_service)
):
    """Protected endpoint: Retrieves the user directory.

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
    usuario_actual: AdminDep, user_service: UserService = Depends(get_user_service)
):
    """Protected endpoint: Retrieves the collection of logically deleted users.

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
    cedula: str, usuario_actual: AdminDep, user_service: UserService = Depends(get_user_service)
):
    """Protected endpoint: Recovers a soft-deleted user account.

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
        target_cedula=cedula, current_user=usuario_actual
    )


# -------------------------------------------------------------------
# SUPERADMIN ENDPOINTS (superadmin only)
# -------------------------------------------------------------------


@superadmin_router.post("/admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def crear_administrador(
    usuario: UserCreateByAdmin,
    usuario_actual: SuperadminDep,
    user_service: UserService = Depends(get_user_service),
):
    """Protected endpoint: Provisions a new administrative account.

    Only a superadmin reaches this handler: the superadmin_router guard decides
    the role before the body is validated, so an admin gets 403 whatever the
    body (ADR-0012, Consequences).

    Args:
        usuario (UserCreateByAdmin): Validated DTO with explicit role definition.
        usuario_actual (User): Authenticated superadmin executing the operation.
        user_service (UserService): Injected business-logic service.

    Returns:
        UserResponse: JSON representation of the newly provisioned account.
    """
    return await user_service.create_administrative_account(
        user_data=usuario, current_user=usuario_actual
    )


router = APIRouter()
router.include_router(public_router)
router.include_router(self_service_router)
router.include_router(admin_router)
router.include_router(superadmin_router)
