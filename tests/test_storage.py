"""Unit tests for the transport-neutral AzureStorageClient upload contract."""

import pytest
from fastapi import HTTPException

from app.core.storage import AzureStorageClient, StagedImage


async def test_upload_image_rejects_non_image_content_type():
    """Freezes the MIME gate: non-image payloads are rejected with 415 before any CDN I/O."""
    client = AzureStorageClient.__new__(AzureStorageClient)
    staged = StagedImage(
        filename="malware.exe",
        content_type="application/octet-stream",
        content=b"payload",
    )

    with pytest.raises(HTTPException) as exc_info:
        await client.upload_image(staged)

    assert exc_info.value.status_code == 415
