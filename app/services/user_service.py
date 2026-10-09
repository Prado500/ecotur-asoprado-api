import jwt
from fastapi import HTTPException, status, BackgroundTasks

from app.core.email import send_verification_email
from app.models.audit import AuditAction
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserCreateByAdmin
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM, \
    create_verification_token
from app.schemas.token import TokenResponse
from app.services.audit_service import AuditService

ROLE_RANK = {UserRole.tourist: 0, UserRole.admin: 1, UserRole.superadmin: 2}


class UserService:
    """
    Encapsulates business logic and rules, validations, and the operational logic of User entity.
    """
    def __init__(self, user_repo: UserRepository, audit_service: AuditService):
        self.user_repo = user_repo
        self.audit_service = audit_service

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

        # 2.  Log Registry (registration)
        await self.audit_service.log_transaction(
            entity_name="User", entity_id=saved_user.cedula,
            action=AuditAction.CREATE, performed_by=saved_user.cedula
        )

        # 3. Generate the single-use token
        token = create_verification_token(saved_user.email)

        # 4. Dispatch the email in the background to prevent blocking the HTTP response
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
        Orchestrates the soft deletion of a user account enforcing hierarchical ABAC.

        Authorization follows a pure hierarchical invariant with self-deletion
        parity: the action is allowed only when the actor deletes their own
        account or when the actor's role rank is strictly greater than the
        target's role rank.

        Args:
            target_cedula (str): The primary identifier of the account to delete.
            current_user (User): The authenticated user attempting the deletion.

        Returns:
            dict: Standardized confirmation payload.

        Raises:
            HTTPException: 404 Not Found if the target doesn't exist.
            HTTPException: 403 Forbidden if the hierarchical invariant fails.
        """
        soft_deleted_user = await self.user_repo.get_user_by_cedula(target_cedula)

        # 1. Handle specific 404 before any role evaluation to prevent AttributeError on None
        if not soft_deleted_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario especificado no existe o ya ha sido eliminado del sistema."
            )

        # 2. ABAC Hierarchical Invariant: self-deletion parity OR strictly higher rank
        is_self_deletion = current_user.cedula == target_cedula
        actor_outranks_target = ROLE_RANK[current_user.role] > ROLE_RANK[soft_deleted_user.role]

        if not is_self_deletion and not actor_outranks_target:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios insuficientes o violación de jerarquía. No tiene autorización para eliminar esta cuenta."
            )

        # 3. Soft-deletion delegated to repository layer
        await self.user_repo.soft_delete_user(target_cedula)

        # 4. Log Registry (soft-deletion)
        await self.audit_service.log_transaction(
            entity_name="User", entity_id=target_cedula,
            action=AuditAction.SOFT_DELETE, performed_by=current_user.cedula
        )

        return {
            "success": True,
            "message": f"La cuenta vinculada a {soft_deleted_user.email}, con C.C. {target_cedula} ha sido eliminada exitosamente."
        }

    async def get_all_registered_users(self, current_user: User) -> list[User]:
        """
        Retrieves the user directory enforcing hierarchical visibility rules.

        Authorization is enforced at the routing boundary (admin-tier
        dependency); this method only applies data-scoping rules: superadmins
        retrieve the entire user base while standard admins receive the
        directory without superadmin entities.

        Args:
            current_user (User): The authenticated administrator executing the
                query. Used to derive visibility scoping, not for authorization.

        Returns:
            list[User]: The scoped list of active User ORM entities.
        """
        users = await self.user_repo.get_all_users()

        # RBAC Visibility Filter: Admins cannot see Superadmins
        if current_user.role == UserRole.admin:
            users = [u for u in users if u.role != UserRole.superadmin]

        return users

    async def update_user_account(self, target_cedula: str, update_data: UserUpdate, current_user: User) -> User:
        """
        Executes a partial update on a user entity enforcing hierarchical ABAC.

        Authorization follows the same mathematical dominance rule used by
        account deletion: self-updates are always permitted, while third-party
        updates require the actor's role rank to be strictly greater than the
        target's role rank. Fail-safe invariants additionally block role
        mutations for non-superadmins and is_active mutations for tourists.

        Args:
            target_cedula (str): The primary identifier of the account to update.
            update_data (UserUpdate): Pydantic DTO containing the fields to modify.
            current_user (User): The authenticated user attempting the mutation.

        Returns:
            User: The refreshed User ORM entity after persistence.

        Raises:
            HTTPException: 404 Not Found if target doesn't exist.
            HTTPException: 403 Forbidden if the hierarchical ABAC invariant or
                any fail-safe field invariant is violated.
        """
        target_user = await self.user_repo.get_user_by_cedula(target_cedula, include_deleted=True)

        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario especificado no existe en la base de datos."
            )

        is_self_update = current_user.cedula == target_cedula

        # 1. ABAC Hierarchical Invariant: self-update parity OR strictly higher rank
        if not is_self_update and ROLE_RANK[current_user.role] <= ROLE_RANK[target_user.role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Violación de jerarquía: No tiene privilegios para modificar a este usuario."
            )

        # 2. Fail-Safe Invariants: noisy privilege guards instead of silent sanitization
        update_dict = update_data.model_dump(mode='json', exclude_unset=True)

        if "role" in update_dict and current_user.role != UserRole.superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Violación de jerarquía: Solo un superadministrador puede modificar roles."
            )

        if "is_active" in update_dict and current_user.role == UserRole.tourist:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios insuficientes. No tiene permisos para modificar el estado de la cuenta."
            )

        # 3. Apply Scalar Mutations
        for key, value in update_dict.items():
            setattr(target_user, key, value)

        # 4. Log Registry
        if update_dict:
            await self.audit_service.log_transaction(
                entity_name="User", entity_id=target_cedula,
                action=AuditAction.UPDATE, performed_by=current_user.cedula, changes=update_dict
            )

        return await self.user_repo.save_user(target_user)

    async def get_deleted_users(self, current_user: User) -> list[User]:
        """
        Retrieves the collection of logically deleted users (Recycle Bin).

        Authorization is enforced at the routing boundary (admin-tier
        dependency); this method only applies data-scoping rules: standard
        admins cannot query deleted superadmin accounts while superadmins
        have unrestricted visibility.

        Args:
            current_user (User): The authenticated administrator executing the
                query. Used to derive visibility scoping, not for authorization.

        Returns:
            list[User]: The scoped list of logically deleted User ORM entities.
        """
        # Query all users bypassing the default active-only filter
        users = await self.user_repo.get_all_users(include_deleted=True)

        # Isolate strictly deleted entities
        deleted_users = [u for u in users if u.deleted_at is not None]

        # RBAC Visibility Filter
        if current_user.role == UserRole.admin:
            deleted_users = [u for u in deleted_users if u.role != UserRole.superadmin]

        return deleted_users

    async def recover_user_account(self, target_cedula: str, current_user: User) -> dict:
        """
        Restores a soft-deleted user account enforcing RBAC precedence.

        Recovered accounts are structurally restored but forced into an inactive
        state (is_active=False) by default, requiring explicit administrative
        approval before network access is granted.

        Args:
            target_cedula (str): The primary identifier of the account to recover.
            current_user (User): The authenticated administrator.

        Returns:
            dict: Standardized confirmation payload.

        Raises:
            HTTPException: 404 Not Found if the user is not in the recycle bin.
            HTTPException: 403 Forbidden if a standard admin attempts to recover a higher-tier account.
        """
        target_user = await self.user_repo.get_user_by_cedula(target_cedula, include_deleted=True)

        if not target_user or target_user.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario no existe o no se encuentra en la papelera."
            )

        # Evaluate Hierarchical Precedence
        if current_user.role == UserRole.admin and target_user.role in [UserRole.admin, UserRole.superadmin]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Violación de jerarquía: No tiene autorización para recuperar esta cuenta."
            )

        # State Mutation
        target_user.deleted_at = None
        target_user.is_active = False
        await self.user_repo.save_user(target_user)

        await self.audit_service.log_transaction(
            entity_name="User", entity_id=target_cedula,
            action=AuditAction.RECOVER, performed_by=current_user.cedula
        )

        return {"success": True, "cc": target_user.cedula, "correo": target_user.email, "nombre": target_user.first_name, "apellido": target_user.last_name, "message": "Usuario recuperado. Se encuentra inactivo por seguridad."}

    async def create_administrative_account(self, user_data: UserCreateByAdmin, current_user: User) -> User:
        """
        Provisions a new administrative account bypassing the public pipeline.

        The superadmin-only guard below is an intentional hierarchical business
        rule, not a duplicate of the transport frontier: the router's admin-tier
        dependency only guarantees an admin+ session, while provisioning accounts
        is reserved for the highest governance tier. The account is created
        instantly without requiring email verification.

        Args:
            user_data (UserCreateByAdmin): DTO containing profile and explicit role definitions.
            current_user (User): The authenticated superadmin executing the creation.

        Returns:
            User: The newly persisted administrative ORM entity.

        Raises:
            HTTPException: 403 Forbidden if the requester is not a superadmin.
            HTTPException: 400 Bad Request if the cedula or email already exists.
        """
        if current_user.role != UserRole.superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Violación de jerarquía: Solo un Superusuario puede aprovisionar cuentas administrativas."
            )

        existing_user = await self.user_repo.get_user_by_email_or_cedula(
            email=user_data.email,
            cedula=user_data.cedula
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico o la cédula ya se encuentran registrados en el sistema."
            )

        # Instantiation leveraging the specific admin DTO
        new_user = User(
            cedula=user_data.cedula,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role,
            data_consent=user_data.data_consent,
            is_active=user_data.is_active
        )

        await self.audit_service.log_transaction(
            entity_name="User", entity_id=user_data.cedula,
            action=AuditAction.CREATE, performed_by=current_user.cedula, changes={"role": user_data.role.value}
        )

        return await self.user_repo.create_user(new_user)