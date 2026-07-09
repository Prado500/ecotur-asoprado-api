from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.token import TokenResponse

class UserService:
    """
    Encapsulates business logic and rules, validations, and the operational logic of User entity.
    """
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_tourist(self, user_data: UserCreate) -> User:
        existing_user = await self.user_repo.get_user_by_email_or_cedula(
            email=user_data.email,
            cedula=user_data.cedula
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este usuario ya se encuentra registrado."
            )

        new_user = User(
            cedula=user_data.cedula,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            password_hash=get_password_hash(user_data.password),
            role=UserRole.tourist,
            data_consent=user_data.data_consent,
            is_active=False
        )
        return await self.user_repo.create_user(new_user)

    async def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_active_user_by_email(credentials.email)

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Revise su correo y contraseña",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debe verificar su cuenta. Revise su correo electrónico.",
            )

        token_payload = {
            "sub": user.email,
            "role": user.role.value
        }

        generated_token = create_access_token(data=token_payload)
        return TokenResponse(access_token=generated_token, token_type="bearer")