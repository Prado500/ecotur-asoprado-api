import os
import uuid
from fastapi import UploadFile, HTTPException, status
from azure.storage.blob.aio import BlobServiceClient

class AzureStorageClient:
    """
    Asynchronous client for interacting with Azure Blob Storage.
    Encapsulates binary upload logic and public URL generation.
    """
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME", "ecotur-images")

        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is missing in environment variables.")

        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

    async def upload_image(self, file: UploadFile) -> str:
        """
        Uploads a binary file stream to Azure and returns its public URL.
        """
        # Validate MIME type to prevent malicious executable uploads
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"El archivo {file.filename} no es una imagen válida."
            )

        # Extract extension and generate UUID to prevent file overriding
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        try:
            # Instantiate clients
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(unique_filename)

            # Stream the file directly to Azure
            file_content = await file.read()
            await blob_client.upload_blob(file_content, overwrite=True)

            return blob_client.url

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fallo al comunicar con Azure CDN: {str(e)}"
            )
        finally:
            # Ensure RAM is freed after streaming
            await file.close()