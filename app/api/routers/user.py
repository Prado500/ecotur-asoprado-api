from fastapi import APIRouter, Depends, status, BackgroundTasks, Request
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import TokenResponse
from app.models.user import User
from app.api.dependencies import get_current_user, get_user_service
from app.services.user_service import UserService

router = APIRouter()

@router.post("/registro", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registrar_turista(
        request: Request,
        usuario: UserCreate,
        background_tasks: BackgroundTasks,
        user_service: UserService = Depends(get_user_service)
):
    """ Delegates User creation to UserService and dispatches verification email in the background. """

    base_url = str(request.base_url).rstrip("/")

    return await user_service.register_tourist(
        user_data=usuario,
        background_tasks=background_tasks,
        base_url=base_url
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