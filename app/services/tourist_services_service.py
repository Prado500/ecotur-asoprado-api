from datetime import datetime, timezone

from fastapi import HTTPException, status
from typing import List

from app.repositories.service_repository import ServiceRepository
from app.models.user import User, UserRole
from app.models.service import TouristService, ServiceImage
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.audit_service import AuditService
from app.models.audit import AuditAction


class TouristServicesService:
    """
        Encapsulates business logic and rules, validations, and the operational logic of TouristService entity.
    """
    def __init__(self, service_repo: ServiceRepository, audit_service: AuditService):
        self.service_repo = service_repo
        self.audit_service = audit_service

    async def create_tourist_package(self, package_data: ServiceCreate, current_user: User) -> TouristService:
        if current_user.role not in [UserRole.admin]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios insuficientes."
            )

        tourist_service_data = package_data.model_dump(exclude={"image_urls"})
        new_tourist_service = TouristService(**tourist_service_data)

        for idx, url in enumerate(package_data.image_urls):
            nueva_imagen = ServiceImage(
                image_url=str(url),
                is_primary=(idx == 0)
            )
            new_tourist_service.images.append(nueva_imagen)

        saved = await self.service_repo.create_service(new_tourist_service)
        await self.audit_service.log_transaction(
            entity_name="TouristService", entity_id=str(saved.id),
            action=AuditAction.CREATE, performed_by=current_user.cedula, changes=package_data.model_dump(mode='json')
        )

        return saved

    async def list_active_packages(self) -> List[TouristService]:
        return await self.service_repo.get_all_active_services()

    def _verify_admin(self, current_user: User) -> None:
        """
        Validates if the provided user possesses administrative privileges.

        This private method acts as a Role-Based Access Control (RBAC) gatekeeper
        to prevent unauthorized mutation or access to sensitive package data.

        Args:
            current_user (User): The user entity extracted from the current JWT session.

        Raises:
            HTTPException: 403 Forbidden if the user's role is not 'admin' or 'superadmin' .
        """
        if current_user.role not in [UserRole.admin, UserRole.superadmin] :
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios insuficientes."
            )

    async def list_inactive_packages(self, current_user: User) -> List[TouristService]:
        """
        Retrieves all tourist packages that are physically present but hidden from the public catalog.

        These packages belong to the 'Por Activar' Kanban column. They have been
        created and are deactivated, but not logically deleted.

        Args:
            current_user (User): The user attempting to access the data. Must be an admin.

        Returns:
            List[TouristService]: A list of inactive package ORM entities.
        """
        self._verify_admin(current_user)
        return await self.service_repo.get_inactive_services()

    async def list_deleted_packages(self, current_user: User) -> List[TouristService]:
        """
        Retrieves all soft-deleted tourist packages (Recycle Bin equivalent).

        These packages belong to the 'Eliminados' Kanban column and are kept
        strictly for historical referential integrity and potential recovery.

        Args:
            current_user (User): The user attempting to access the data. Must be an admin.

        Returns:
            List[TouristService]: A list of logically deleted package ORM entities.
        """
        self._verify_admin(current_user)
        return await self.service_repo.get_deleted_services()

    async def toggle_package_status(self, service_id: int, is_available: bool, current_user: User) -> dict:
        """
        Mutates the public availability state of a specific non-soft-deleted package.

        Transitions a package between the 'Por Activar' and 'Activos' columns.

        Args:
            service_id (int): The unique identifier of the package.
            is_available (bool): The target availability state (True for active, False for inactive).
            current_user (User): The administrator executing the mutation.

        Returns:
            dict: A standardized JSON response confirming the state change.

        Raises:
            HTTPException: 404 Not Found if the package does not exist or is deleted.
        """
        self._verify_admin(current_user)
        service = await self.service_repo.get_service_by_id(service_id)

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete no encontrado."
            )

        service.is_available = is_available
        await self.service_repo.save_service(service)



        action = AuditAction.ACTIVATE if is_available else AuditAction.DEACTIVATE
        await self.audit_service.log_transaction(
            entity_name="TouristService", entity_id=str(service_id),
            action=action, performed_by=current_user.cedula
        )

        estado = "activado" if is_available else "desactivado"

        return {"success": True, "message": f"El paquete ha sido {estado} exitosamente."}

    async def soft_delete_package(self, service_id: int, current_user: User) -> dict:
        """
        Executes a soft deletion on a package to preserve its financial historical footprint.

        Transitions the package to the 'Eliminados' column by stamping the UTC timestamp
        and forcefully setting its availability to False to unpublish it instantly.

        Args:
            service_id (int): The unique identifier of the package to delete.
            current_user (User): The administrator executing the deletion.

        Returns:
            dict: Standardized confirmation message.

        Raises:
            HTTPException: 404 Not Found if the package is already deleted or doesn't exist.
        """
        self._verify_admin(current_user)
        service = await self.service_repo.get_service_by_id(service_id)

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete no encontrado."
            )

        # State Mutation Flow
        service.deleted_at = datetime.now(timezone.utc)
        service.is_available = False

        await self.service_repo.save_service(service)
        await self.audit_service.log_transaction(
            entity_name="TouristService", entity_id=str(service_id),
            action=AuditAction.SOFT_DELETE, performed_by=current_user.cedula
        )
        return {"success": True, "message": "Paquete movido a la papelera (Eliminado lógicamente).", "UID": service_id}

    async def recover_package(self, service_id: int, current_user: User) -> dict:
        """
        Restores a soft-deleted package back to the operational workflow.

        As a business rule, recovered packages strictly transition to the 'Por Activar'
        column (`is_available = False`) to prevent accidental public exposure without review.

        Args:
            service_id (int): The unique identifier of the deleted package.
            current_user (User): The administrator performing the recovery.

        Returns:
            dict: Standardized confirmation message.

        Raises:
            HTTPException: 400 Bad Request if the package was not actually deleted.
        """
        self._verify_admin(current_user)

        # Override the default repository scope to include soft-deleted records
        service = await self.service_repo.get_service_by_id(service_id, include_deleted=True)

        if not service or service.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El paquete no está en la papelera ('Eliminados')."
            )

        # Architectural Rule: Prevent automatic publishing upon recovery
        service.deleted_at = None
        service.is_available = False

        await self.service_repo.save_service(service)

        await self.audit_service.log_transaction(
            entity_name="TouristService", entity_id=str(service_id),
            action=AuditAction.RECOVER, performed_by=current_user.cedula
        )

        return {"success": True, "message": "Paquete recuperado. Se encuentra en la sección 'Por Activar'.", "UID": service_id}

    async def update_package_details(self, service_id: int, update_data: ServiceUpdate, current_user: User) -> TouristService:
        """
        Applies a partial or complete scalar update to an existing package.

        Implements SQLAlchemy's 'delete-orphan' cascade by clearing the image
        relationship array and re-instantiating it, ensuring absolute sync
        with the incoming payload.

        Args:
            service_id (int): The target package ID.
            update_data (ServiceUpdate): Partial DTO containing only modified fields.
            current_user (User): The administrator executing the update.

        Returns:
            TouristService: The refreshed ORM instance after the database commit.

        Raises:
            HTTPException: 404 Not Found if the target package is unavailable.
        """
        self._verify_admin(current_user)
        service = await self.service_repo.get_service_by_id(service_id)

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete no encontrado. Está deshabilitado (deleted_at != None) o no exíste."
            )

        # 1. Update primitive fields (Scalar Mutation)
        update_dict = update_data.model_dump(exclude_unset=True, exclude={"image_urls"})
        for key, value in update_dict.items():
            setattr(service, key, value)

        # 2. Update relational fields (Destruction and Re-creation paradigm)
        if update_data.image_urls is not None:
            # Clearing triggers Alembic's cascade deletion of old images
            service.images.clear()
            for idx, url in enumerate(update_data.image_urls):
                nueva_imagen = ServiceImage(image_url=str(url), is_primary=(idx == 0))
                service.images.append(nueva_imagen)

        payload_changes = update_data.model_dump(mode='json', exclude_unset=True)
        if payload_changes:
            await self.audit_service.log_transaction(
                entity_name="TouristService", entity_id=str(service_id),
                action=AuditAction.UPDATE, performed_by=current_user.cedula, changes=payload_changes
            )

        return await self.service_repo.save_service(service)