import os
import uuid
from typing import NamedTuple

from fastapi import HTTPException, status
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings


class StagedImage(NamedTuple):
    """
    Transport-neutral in-memory representation of an uploaded image.

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
    """
    Asynchronous client for interacting with Azure Blob Storage.
    Encapsulates binary upload logic and public URL generation.
    """
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME", "ecotur-images")
        self.temporal_container_name = os.getenv("AZURE_TEMPORAL_CONTAINER_NAME", "temp-ecotur-images")

        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is missing in environment variables.")

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

    async def upload_image(self, image: StagedImage) -> str:
        """
        Uploads a staged in-memory image to Azure and returns its public URL.

        Args:
            image (StagedImage): Buffered image payload with its filename and MIME type.

        Returns:
            str: Public URL of the blob once stored in the temporal container.

        Raises:
            HTTPException: 415 when the MIME type is not an image, or 500 when
                the Azure CDN communication fails.
        """
        # Validate MIME type to prevent malicious executable uploads
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"El archivo {image.filename} no es una imagen válida."
            )

        # Extract extension and generate UUID to prevent file overriding
        file_extension = image.filename.split(".")[-1] if "." in image.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        try:
            # Instantiate clients
            container_client = self.blob_service_client.get_container_client(self.temporal_container_name)
            blob_client = container_client.get_blob_client(unique_filename)

            # Stream the staged bytes directly to Azure
            file_content = image.content

            # Explicitly instruct Azure to serve this blob as an image,
            # allowing browsers to render it inline instead of forcing a download.
            image_content_settings = ContentSettings(content_type=image.content_type)

            await blob_client.upload_blob(file_content, overwrite=True, content_settings=image_content_settings)

            return blob_client.url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fallo al comunicar con Azure CDN: {str(e)}"
            )

    async def delete_image(self, file_url: str):
        """
        Deletes a blob directly from the CDN using its public URL.
        """
        try:
            # Extraction of uuid  (e.g. it retrieves "3247t74t3.jpg" out of "https://.../contenedor/3247t74t3.jpg")
            blob_name = file_url.split("/")[-1]

            # Instantiate clients
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            await blob_client.delete_blob()
        except Exception as e:
            print(f"Warning: No se pudo borrar el blob {file_url} del CDN. Detalle: {e}")

    async def promote_to_permanent(self, temp_url: str) -> str:
        """
        Populates a blob image from the temporal CDN container to the permanent CDN container.
        """
        try:

            # We get the confirmed blob's UUID
            blob_name = temp_url.split("/")[-1]


            # We instance both container clients
            temp_container = self.blob_service_client.get_container_client(self.temporal_container_name)
            perm_container = self.blob_service_client.get_container_client(self.container_name)

            # Provisioning of the blob name parameter
            source_blob = temp_container.get_blob_client(blob_name)
            dest_blob = perm_container.get_blob_client(blob_name)

            # 1.) Copy and write the blob's bytes inside the permanent container via the URL coming from the temporal container.
            await dest_blob.start_copy_from_url(temp_url)


            await source_blob.delete_blob()


            return dest_blob.url

        except Exception as e:
            print(f"Error al promover la imagen {temp_url}: {e}")
            # Si falla, devolvemos la URL temporal para no romper el flujo,
            # o levantamos excepción según tu regla de negocio.
            raise HTTPException(status_code=500, detail="Fallo al consolidar las imágenes en el CDN.")