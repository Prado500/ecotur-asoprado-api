import jwt
from fastapi import HTTPException, status, BackgroundTasks

from app.core.email import send_verification_email
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserUpdate
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

    async def get_all_registered_users(self, current_user: User) -> list[User]:
        """
        Retrieves the user directory enforcing hierarchical visibility rules.

        Superadmins retrieve the entire user base. Regular admins retrieve
        the user base excluding superadmin accounts to prevent unauthorized
        visibility into higher-tier governance.

        Args:
            current_user (User): The authenticated user making the request.

        Returns:
            list[User]: A filtered list of User ORM entities.

        Raises:
            HTTPException: 403 Forbidden if the requester is a standard tourist.
        """
        if current_user.role == UserRole.tourist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios insuficientes para acceder al directorio de usuarios."
            )

        users = await self.user_repo.get_all_users()

        # RBAC Visibility Filter: Admins cannot see Superadmins
        if current_user.role == UserRole.admin:
            users = [u for u in users if u.role != UserRole.superadmin]

        return users

    async def update_user_account(self, target_cedula: str, update_data: UserUpdate, current_user: User) -> User:
        """
        Executes a partial update on a user entity enforcing strict RBAC precedence rules.

        Implements a Hybrid RBAC approach:
        1. Users can self-update their basic profile data.
        2. Admins can update tourists (Helpdesk pattern) but cannot modify higher tiers.
        3. Superadmins possess unrestricted update authority.

        Args:
            target_cedula (str): The primary identifier of the account to update.
            update_data (UserUpdate): Pydantic DTO containing the fields to modify.
            current_user (User): The authenticated user attempting the mutation.

        Returns:
            User: The refreshed User ORM entity after persistence.

        Raises:
            HTTPException: 404 Not Found if target doesn't exist.
            HTTPException: 403 Forbidden if RBAC precedence rules are violated.
        """
        target_user = await self.user_repo.get_user_by_cedula(target_cedula, include_deleted=True)

        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario especificado no existe en la base de datos."
            )

        is_self_update = (current_user.cedula == target_cedula)

        # 1. Evaluate Hierarchical Precedence
        if not is_self_update:
            if current_user.role == UserRole.tourist:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Privilegios insuficientes. Los turistas no pueden modificar otras cuentas."
                )

            # An admin attempting to modify another admin or superadmin
            if current_user.role == UserRole.admin and target_user.role in [UserRole.admin, UserRole.superadmin]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Violación de jerarquía: Un administrador no puede modificar cuentas de su mismo o mayor nivel."
                )

        # 2. Payload Sanitization
        update_dict = update_data.model_dump(exclude_unset=True)

        # Defensive sanitization: Ensure self-updating tourists cannot escalate privileges or revive banned accounts
        if is_self_update and current_user.role == UserRole.tourist:
            update_dict.pop("role", None)
            update_dict.pop("is_active", None)

        # 3. Apply Scalar Mutations
        for key, value in update_dict.items():
            setattr(target_user, key, value)

        return await self.user_repo.save_user(target_user)