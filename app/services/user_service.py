import jwt
from fastapi import HTTPException, status, BackgroundTasks

from app.core.email import send_verification_email
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM, \
    create_verification_token
from app.schemas.token import TokenResponse

class UserService:
    """
    Encapsulates business logic and rules, validations, and the operational logic of User entity.
    """
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_tourist(self, user_data: UserCreate, background_tasks: BackgroundTasks, base_url: str) -> User:
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

        # 1. Persist the inactive user
        saved_user = await self.user_repo.create_user(new_user)

        # 2. Generate the single-use token
        token = create_verification_token(saved_user.email)

        # 3. Dispatch the email in the background to prevent blocking the HTTP response
        background_tasks.add_task(
            send_verification_email,
            email_to=saved_user.email,
            first_name=saved_user.first_name,
            token=token,
            base_url=base_url
        )

        return saved_user


    async def verify_email_account(self, token: str) -> dict:
        """
        Decodes the verification token and activates the user account.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            scope: str = payload.get("scope")

            if email is None or scope != "email_verification":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de verificación inválido.")

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace de verificación ha expirado. Por favor solicite uno nuevo.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de verificación inválido o corrupto.")

        activation_success = await self.user_repo.activate_user(email)

        if not activation_success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        return {"success": True, "message": "Cuenta verificada exitosamente. Ya puede iniciar sesión."}


    async def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_non_deleted_user_by_email(credentials.email)

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

    async def delete_user_account(self, target_cedula: str, current_user: User) -> dict:
        """
        Orchestrates the soft deletion of a user account enforcing RBAC.
        Only an Administrator or the owner of the account can trigger this action.
        """
        # 1. RBAC Security Check
        if current_user.role != UserRole.admin and current_user.cedula != target_cedula:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios insuficientes. No tiene autorización para eliminar esta cuenta."
            )

        # 2. Database Delegation
        soft_deleted_user = await self.user_repo.soft_delete_user(target_cedula)

        # 3. Handle specific 404
        if not soft_deleted_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario especificado no existe o ya ha sido eliminado del sistema."
            )

        return {
            "success": True,
            "message": f"La cuenta vinculada a {soft_deleted_user.email}, con C.C. {target_cedula} ha sido eliminada exitosamente."
        }