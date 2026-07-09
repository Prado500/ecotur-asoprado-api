from fastapi import APIRouter, Depends, status
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import TokenResponse
from app.models.user import User
from app.api.dependencies import get_current_user, get_user_service
from app.services.user_service import UserService

router = APIRouter()

@router.post("/registro", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registrar_turista(
        usuario: UserCreate,
        user_service: UserService = Depends(get_user_service)
):
    """ Delegates User creation to UserService.
        Returns a JSON representation containing
        general information of a registered User.
    """
    return await user_service.register_tourist(usuario)


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