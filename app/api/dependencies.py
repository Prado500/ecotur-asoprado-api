import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.schemas.token import TokenData
from app.core.security import SECRET_KEY, ALGORITHM

# Repository injection
from app.repositories.user_repository import UserRepository
from app.repositories.service_repository import ServiceRepository

# Service injection
from app.services.user_service import UserService
from app.services.tourist_services_service import TouristServicesService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

# --- DEPENDENCY FACTORY (Inversion of Control) ---

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_tourist_services_repository(db: AsyncSession = Depends(get_db)) -> ServiceRepository:
    return ServiceRepository(db)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)

def get_service_service(service_repo: ServiceRepository = Depends(get_tourist_services_repository)) -> TouristServicesService:
    return TouristServicesService(service_repo)

# --- ENDPOINT ACCESS CONTROL ---

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Decodes the given JWT token, verifies payload consistency, lifespan status (unexpired or expired)
    and user enabling (only active users are allowed).

    It's injected with a UserRepository instance for user-state consulting against the persistence layer.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la autenticidad de sus credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Su sesión ha expirado. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception

    # UserRepository is delegated to run the query
    usuario = await user_repo.get_active_user_by_email(token_data.email)

    if usuario is None or not usuario.is_active:
        raise credentials_exception

    return usuario