import os
import uuid
from typing import NamedTuple

from azure.core.exceptions import AzureError
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient

from app.core.exceptions import (
    InvalidImageUrlError,
    StorageUnavailableError,
    UnsupportedMediaTypeError,
)


class StagedImage(NamedTuple):
    """Transport-neutral in-memory representation of an uploaded image.

    The API transport (routers) is responsible for reading the multipart
    stream into plain bytes, so this infrastructure layer never depends on
    FastAPI's UploadFile contract.

    Attributes:
        filename (str): Original client-provided file name.
        content_type (str): MIME type declared by the client.
        content (bytes): Fully buffered binary payload.
    """

    filename: str
    content_type: str
    content: bytes


class AzureStorageClient:
    """Asynchronous client for interacting with Azure Blob Storage.

    Encapsulates binary upload logic and public URL generation. Failures are
    reported as domain errors, never as HTTP exceptions.
    """

    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME", "ecotur-images")
        self.temporal_container_name = os.getenv(
            "AZURE_TEMPORAL_CONTAINER_NAME", "temp-ecotur-images"
        )

        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is missing in environment variables.")

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

    def _is_direct_blob_of(self, url: str, container_name: str) -> bool:
        """Tells whether a URL is a direct blob of a container of this account.

        Args:
            url (str): Candidate blob URL.
            container_name (str): Container expected to hold the blob.

        Returns:
            bool: True when the URL starts with the exact container URL and the
                remainder is a non-empty name without '/' or '?'.
        """
        prefix = f"{self.blob_service_client.get_container_client(container_name).url}/"
        if not url.startswith(prefix):
            return False
        blob_name = url[len(prefix) :]
        return bool(blob_name) and "/" not in blob_name and "?" not in blob_name

    def is_temporal_url(self, url: str) -> bool:
        """Tells whether a URL is a blob of this account's temporal container.

        Args:
            url (str): Candidate blob URL.

        Returns:
            bool: True when the URL is a direct blob of the temporal container.
        """
        return self._is_direct_blob_of(url, self.temporal_container_name)

    def is_permanent_url(self, url: str) -> bool:
        """Tells whether a URL is a blob of this account's permanent container.

        Args:
            url (str): Candidate blob URL.

        Returns:
            bool: True when the URL is a direct blob of the permanent container.
        """
        return self._is_direct_blob_of(url, self.container_name)

    async def upload_image(self, image: StagedImage) -> str:
        """Uploads a staged in-memory image to Azure and returns its public URL.

        Args:
            image (StagedImage): Buffered image payload with its filename and MIME type.

        Returns:
            str: Public URL of the blob once stored in the temporal container.

        Raises:
            UnsupportedMediaTypeError: When the MIME type is not an image.
            StorageUnavailableError: When the Azure CDN communication fails.
        """
        # Validate MIME type to prevent malicious executable uploads
        if not image.content_type.startswith("image/"):
            raise UnsupportedMediaTypeError(
                detail=f"El archivo {image.filename} no es una imagen válida."
            )

        # Extract extension and generate UUID to prevent file overriding
        file_extension = image.filename.split(".")[-1] if "." in image.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        try:
            # Instantiate clients
            container_client = self.blob_service_client.get_container_client(
                self.temporal_container_name
            )
            blob_client = container_client.get_blob_client(unique_filename)

            # Stream the staged bytes directly to Azure
            file_content = image.content

            # Explicitly instruct Azure to serve this blob as an image,
            # allowing browsers to render it inline instead of forcing a download.
            image_content_settings = ContentSettings(content_type=image.content_type)

            await blob_client.upload_blob(
                file_content, overwrite=True, content_settings=image_content_settings
            )

            return blob_client.url

        except AzureError as e:
            raise StorageUnavailableError(
                detail=f"Fallo al comunicar con Azure CDN: {str(e)}"
            ) from e

    async def delete_image(self, file_url: str):
        """Deletes a blob directly from the CDN using its public URL.

        Args:
            file_url (str): Public URL of the blob in the permanent container.
        """
        try:
            # Extraction of uuid (e.g. "3247t74t3.jpg" out of "https://.../contenedor/3247t74t3.jpg")
            blob_name = file_url.split("/")[-1]

            # Instantiate clients
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            await blob_client.delete_blob()
        except Exception as e:
            print(f"Warning: No se pudo borrar el blob {file_url} del CDN. Detalle: {e}")

    async def promote_to_permanent(self, temp_url: str) -> str:
        """Copies a blob from the temporal container to the permanent one.

        The source is deleted only after Azure confirms the copy finished
        (``copy_status == "success"``), so an unfinished copy never loses the blob.

        Args:
            temp_url (str): URL of a blob in this account's temporal container.

        Returns:
            str: URL of the blob in the permanent container.

        Raises:
            InvalidImageUrlError: When the URL is not a blob of the temporal
                container or the source blob does not exist.
            StorageUnavailableError: When Azure fails or the copy did not finish.
        """
        if not self.is_temporal_url(temp_url):
            raise InvalidImageUrlError(
                detail="La imagen debe provenir del contenedor temporal de imágenes."
            )

        try:
            # We get the confirmed blob's UUID
            blob_name = temp_url.split("/")[-1]

            # We instance both container clients
            temp_container = self.blob_service_client.get_container_client(
                self.temporal_container_name
            )
            perm_container = self.blob_service_client.get_container_client(self.container_name)

            # Provisioning of the blob name parameter
            source_blob = temp_container.get_blob_client(blob_name)
            dest_blob = perm_container.get_blob_client(blob_name)

            if not await source_blob.exists():
                raise InvalidImageUrlError(detail="La imagen indicada no existe en el CDN.")

            # Synchronous copy: Azure answers only once the bytes are in place.
            props = await dest_blob.start_copy_from_url(temp_url, requires_sync=True)
            if props.get("copy_status") != "success":
                raise StorageUnavailableError(detail="Fallo al consolidar las imágenes en el CDN.")

            await source_blob.delete_blob()

            return dest_blob.url

        except AzureError as e:
            print(f"Error al promover la imagen {temp_url}: {e}")
            raise StorageUnavailableError(
                detail="Fallo al consolidar las imágenes en el CDN."
            ) from e
