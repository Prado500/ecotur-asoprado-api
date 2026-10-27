import asyncio
from datetime import UTC, datetime

from pydantic import HttpUrl

from app.core.exceptions import BusinessRuleViolationError, InvalidImageUrlError, NotFoundError
from app.core.storage import AzureStorageClient, StagedImage
from app.models.audit import AuditAction
from app.models.service import ServiceImage, TouristService
from app.models.user import User
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.audit_service import AuditService


class TouristServicesService:
    """Encapsulates business rules and operational logic of the TouristService entity."""

    def __init__(
        self,
        service_repo: ServiceRepository,
        audit_service: AuditService,
        storage_client: AzureStorageClient,
    ):
        self.service_repo = service_repo
        self.audit_service = audit_service
        self.storage_client = storage_client

    async def create_tourist_package(
        self, package_data: ServiceCreate, current_user: User
    ) -> TouristService:
        """Creates a package, promoting its staged images to the permanent container.

        A new package only accepts blobs of the temporal container (uploaded first through
        the staging endpoint); any other URL is rejected before touching the CDN.

        Args:
            package_data: Validated creation payload, including the image URLs.
            current_user: Administrator performing the operation (audit trail).

        Returns:
            TouristService: The persisted package with its images.

        Raises:
            BusinessRuleViolationError: If more than 10 images are supplied.
            InvalidImageUrlError: If an image is not a temporal blob, or it no longer exists.
            StorageUnavailableError: If the CDN fails while promoting an image.
        """
        if len(package_data.image_urls) > 10:
            raise BusinessRuleViolationError(
                detail="El número de imágenes a subir excede el límite permitido por paquete (10). "
            )

        tourist_service_data = package_data.model_dump(exclude={"image_urls"})
        new_tourist_service = TouristService(**tourist_service_data)

        for idx, url in enumerate(package_data.image_urls):
            raw_url = str(url)
            if not self.storage_client.is_temporal_url(raw_url):
                raise InvalidImageUrlError(
                    detail="La imagen debe subirse primero por /servicios/upload-images/."
                )
            persistent_url = await self.storage_client.promote_to_permanent(raw_url)

            nueva_imagen = ServiceImage(image_url=persistent_url, is_primary=(idx == 0))
            new_tourist_service.images.append(nueva_imagen)

        saved = await self.service_repo.create_service(new_tourist_service)

        await self.audit_service.log_transaction(
            entity_name="TouristService",
            entity_id=str(saved.id),
            action=AuditAction.CREATE,
            performed_by=current_user.cedula,
            changes=package_data.model_dump(mode="json"),
        )

        return saved

    async def list_active_packages(self) -> list[TouristService]:
        return await self.service_repo.get_all_active_services()

    async def list_inactive_packages(self) -> list[TouristService]:
        """Retrieves all packages that are present but hidden from the public catalog.

        These packages belong to the 'Por Activar' Kanban column. They have been
        created and are deactivated, but not logically deleted.

        Returns:
            List[TouristService]: A list of inactive package ORM entities.
        """
        return await self.service_repo.get_inactive_services()

    async def list_deleted_packages(self) -> list[TouristService]:
        """Retrieves all soft-deleted tourist packages (Recycle Bin equivalent).

        These packages belong to the 'Eliminados' Kanban column and are kept
        strictly for historical referential integrity and potential recovery.

        Returns:
            List[TouristService]: A list of logically deleted package ORM entities.
        """
        return await self.service_repo.get_deleted_services()

    async def toggle_package_status(
        self, service_id: int, is_available: bool, current_user: User
    ) -> dict:
        """Mutates the public availability state of a specific non-soft-deleted package.

        Transitions a package between the 'Por Activar' and 'Activos' columns.

        Args:
            service_id (int): The unique identifier of the package.
            is_available (bool): Target availability (True for active, False for inactive).
            current_user (User): The administrator executing the mutation.

        Returns:
            dict: A standardized JSON response confirming the state change.

        Raises:
            NotFoundError: If the package does not exist or is deleted.
        """
        service = await self.service_repo.get_service_by_id(service_id)

        if not service:
            raise NotFoundError(detail="Paquete no encontrado.")

        service.is_available = is_available
        await self.service_repo.save_service(service)

        action = AuditAction.ACTIVATE if is_available else AuditAction.DEACTIVATE
        await self.audit_service.log_transaction(
            entity_name="TouristService",
            entity_id=str(service_id),
            action=action,
            performed_by=current_user.cedula,
        )

        estado = "activado" if is_available else "desactivado"

        return {"success": True, "message": f"El paquete ha sido {estado} exitosamente."}

    async def soft_delete_package(self, service_id: int, current_user: User) -> dict:
        """Executes a soft deletion on a package to preserve its financial historical footprint.

        Transitions the package to the 'Eliminados' column by stamping the UTC timestamp
        and forcefully setting its availability to False to unpublish it instantly.

        Args:
            service_id (int): The unique identifier of the package to delete.
            current_user (User): The administrator executing the deletion.

        Returns:
            dict: Standardized confirmation message.

        Raises:
            NotFoundError: If the package is already deleted or doesn't exist.
        """
        service = await self.service_repo.get_service_by_id(service_id)

        if not service:
            raise NotFoundError(detail="Paquete no encontrado.")

        # State Mutation Flow
        service.deleted_at = datetime.now(UTC)
        service.is_available = False

        await self.service_repo.save_service(service)
        await self.audit_service.log_transaction(
            entity_name="TouristService",
            entity_id=str(service_id),
            action=AuditAction.SOFT_DELETE,
            performed_by=current_user.cedula,
        )
        return {
            "success": True,
            "message": "Paquete movido a la papelera (Eliminado lógicamente).",
            "UID": service_id,
        }

    async def recover_package(self, service_id: int, current_user: User) -> dict:
        """Restores a soft-deleted package back to the operational workflow.

        As a business rule, recovered packages strictly transition to the 'Por Activar'
        column (`is_available = False`) to prevent accidental public exposure without review.

        Args:
            service_id (int): The unique identifier of the deleted package.
            current_user (User): The administrator performing the recovery.

        Returns:
            dict: Standardized confirmation message.

        Raises:
            BusinessRuleViolationError: If the package was not actually deleted.
        """
        # Override the default repository scope to include soft-deleted records
        service = await self.service_repo.get_service_by_id(service_id, include_deleted=True)

        if not service or service.deleted_at is None:
            raise BusinessRuleViolationError(
                detail="El paquete no está en la papelera ('Eliminados')."
            )

        # Architectural Rule: Prevent automatic publishing upon recovery
        service.deleted_at = None
        service.is_available = False

        await self.service_repo.save_service(service)

        await self.audit_service.log_transaction(
            entity_name="TouristService",
            entity_id=str(service_id),
            action=AuditAction.RECOVER,
            performed_by=current_user.cedula,
        )

        return {
            "success": True,
            "message": "Paquete recuperado. Se encuentra en la sección 'Por Activar'.",
            "UID": service_id,
        }

    async def image_uploader(self, images_files: list[StagedImage]) -> dict:
        """Uploads images asynchronously to the Azure CDN.

        Args:
            images_files (List[StagedImage]): List of staged images to be uploaded.

        Returns:
            dict: a ServiceImageOutput compliant dictionary with the urls of the uploaded blobs.

        Raises:
            BusinessRuleViolationError: If more than 10 images are staged in a single request.
            UnsupportedMediaTypeError: If a staged file is not an image.
            StorageUnavailableError: If the Azure CDN is unavailable while uploading.
        """
        if len(images_files) > 10:
            raise BusinessRuleViolationError(
                detail="El número de imágenes a subir excede el límite permitido por paquete (10). "
            )

        blob_urls: list[str] = []
        for image_chunk in images_files:
            fresh_url = await self.storage_client.upload_image(image_chunk)
            blob_urls.append(fresh_url)

        return {"image_urls": blob_urls}

    async def update_package_details(
        self, service_id: int, update_data: ServiceUpdate, current_user: User
    ) -> TouristService:
        """Applies a partial or complete scalar update to an existing package.

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
            NotFoundError: If the target package is unavailable.

        """
        service = await self.service_repo.get_service_by_id(service_id)

        if not service:
            raise NotFoundError(
                detail="Paquete no encontrado. Está deshabilitado (deleted_at != None) o no exíste."
            )

        # 1. Update primitive fields (Scalar Mutation)
        update_dict = update_data.model_dump(exclude_unset=True, exclude={"image_urls"})
        for key, value in update_dict.items():
            setattr(service, key, value)

        # 2. Update relational fields (Destruction and Re-creation paradigm)
        if update_data.image_urls is not None:
            # 2.1 Verify that there is room for those new images and throw exception if not.
            if len(update_data.image_urls) > 10:
                raise BusinessRuleViolationError(
                    detail=(
                        "El número de imágenes a subir excede el límite permitido "
                        "por paquete (10). "
                    )
                )

            # 2.2 Set up image comparison basis and delete removed images (if there's any)
            old_images_urls = {str(img.image_url) for img in service.images}
            new_images_urls = set(str(url) for url in update_data.image_urls)
            urls_to_delete = old_images_urls - new_images_urls

            if urls_to_delete:
                delete_ops = [self.storage_client.delete_image(url) for url in urls_to_delete]
                await asyncio.gather(*delete_ops)

            # 2.3 Clearing triggers Alembic's cascade deletion of old images
            service.images.clear()

            # 2.4 Async function employed to provision image persistence coroutines
            async def resolve_url(url: HttpUrl) -> str:
                if self.storage_client.temporal_container_name in str(url):
                    return await self.storage_client.promote_to_permanent(str(url))
                else:
                    return str(url)

            # 2.5 Resolve the images concurrently (sanitizing non-permanent urls)
            image_resolution_coroutines = [resolve_url(url) for url in update_data.image_urls]

            # 2.6 Execute image resolution coroutines and retrieve definitive image urls
            definitive_urls = await asyncio.gather(*image_resolution_coroutines)

            # 2.7 Append each definitive image url to the edited service
            for idx, url in enumerate(definitive_urls):
                nueva_imagen = ServiceImage(image_url=str(url), is_primary=(idx == 0))
                service.images.append(nueva_imagen)

        # 3. Register changes made on audit table
        payload_changes = update_data.model_dump(mode="json", exclude_unset=True)
        if payload_changes:
            await self.audit_service.log_transaction(
                entity_name="TouristService",
                entity_id=str(service_id),
                action=AuditAction.UPDATE,
                performed_by=current_user.cedula,
                changes=payload_changes,
            )

        return await self.service_repo.save_service(service)
