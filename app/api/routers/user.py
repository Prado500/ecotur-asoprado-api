import os

from fastapi import APIRouter, Depends, status, BackgroundTasks
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserUpdate
from app.schemas.token import TokenResponse
from app.models.user import User
from app.api.dependencies import get_current_user, get_user_service
from app.services.user_service import UserService

router = APIRouter()

@router.post("/registro", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registrar_turista(
        usuario: UserCreate,
        background_tasks: BackgroundTasks,
        user_service: UserService = Depends(get_user_service)
):
    """ Delegates User creation to UserService and dispatches verification email in the background. """

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")

    return await user_service.register_tourist(
        user_data=usuario,
        background_tasks=background_tasks,
        base_url=frontend_url
    )

@router.get("/verificar-email", status_code=status.HTTP_200_OK)
async def verificar_cuenta(
        token: str,
        user_service: UserService = Depends(get_user_service)
):
    """
    Public Endpoint: Decodes the JWT token sent via email and activates the user account.
    Returns a success message JSON.
    """
    return await user_service.verify_email_account(token)


@router.post("/login", response_model=TokenResponse)
async def login(
        credenciales: UserLogin,
        user_service: UserService = Depends(get_user_service)
):
    """ Delegates authentication and JWT provisioning to UserService.
        Returns a signed and temporal JWT token for general access
        to protected resources.
    """
    return await user_service.authenticate_user(credenciales)


@router.get("/mi-perfil", response_model=UserResponse)
async def ver_mi_perfil(usuario_actual: User = Depends(get_current_user)):
    """ Protected Endpoint: Returns generic data of a registered user. """
    return usuario_actual


@router.delete("/{cedula}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(
        cedula: str,
        user_service: UserService = Depends(get_user_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Performs a soft-delete on a target user account.
    Requires Admin privileges or Self-Ownership.
    """
    return await user_service.delete_user_account(
        target_cedula=cedula,
        current_user=usuario_actual
    )

@router.get("/", response_model=list[UserResponse])
async def listar_usuarios(
        user_service: UserService = Depends(get_user_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Retrieves the user directory.

    Delegates hierarchical visibility rules to the UserService to ensure
    Standard Admins cannot retrieve Superadmin entities.
    Requires an active JWT session.
    """
    return await user_service.get_all_registered_users(usuario_actual)

@router.patch("/{cedula}", response_model=UserResponse)
async def actualizar_usuario(
        cedula: str,
        update_data: UserUpdate,
        user_service: UserService = Depends(get_user_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Updates a specific user's profile information.

    Delegates strict RBAC precedence and self-service rules to the UserService.
    Expects a partial JSON payload (PATCH behavior).
    Requires an active JWT session.
    """
    return await user_service.update_user_account(
        target_cedula=cedula,
        update_data=update_data,
        current_user=usuario_actual
    )