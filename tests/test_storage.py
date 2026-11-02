"""Unit tests for AzureStorageClient: MIME gate, URL whitelist, synchronous copy, error mapping."""

from unittest.mock import create_autospec, patch

import pytest
from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.storage.blob.aio import BlobClient, BlobServiceClient, ContainerClient

import app.core.storage as storage_module
from app.core.exceptions import (
    InvalidImageUrlError,
    StorageUnavailableError,
    UnsupportedMediaTypeError,
)
from app.core.storage import AzureStorageClient, StagedImage

ACCOUNT_URL = "https://account.blob.core.windows.net"
TEMP_URL = f"{ACCOUNT_URL}/temp-ecotur-images"
PERM_URL = f"{ACCOUNT_URL}/ecotur-images"


def _blob(url: str):
    """Builds an autospecced async BlobClient with a fixed URL."""
    blob = create_autospec(BlobClient, instance=True)
    blob.url = url
    return blob


def _container(url: str):
    """Builds an autospecced async ContainerClient with a fixed URL."""
    container = create_autospec(ContainerClient, instance=True)
    container.url = url
    return container


class StorageDoubles:
    """Autospecced Azure doubles wired behind a real AzureStorageClient."""

    def __init__(self):
        self.client: AzureStorageClient
        self.temp_container = _container(TEMP_URL)
        self.perm_container = _container(PERM_URL)
        self.source_blob = _blob(f"{TEMP_URL}/abc.jpg")
        self.dest_blob = _blob(f"{PERM_URL}/abc.jpg")
        self.temp_container.get_blob_client.return_value = self.source_blob
        self.perm_container.get_blob_client.return_value = self.dest_blob
        self.dest_blob.start_copy_from_url.return_value = {"copy_status": "success"}
        self.source_blob.exists.return_value = True


@pytest.fixture
def doubles(monkeypatch):
    """Builds an AzureStorageClient over autospecced Azure SDK clients."""
    monkeypatch.setenv("AZURE_STORAGE_CONNECTION_STRING", "UseDevelopmentStorage=true")
    monkeypatch.setenv("AZURE_CONTAINER_NAME", "ecotur-images")
    monkeypatch.setenv("AZURE_TEMPORAL_CONTAINER_NAME", "temp-ecotur-images")
    d = StorageDoubles()
    service = create_autospec(BlobServiceClient, instance=True)
    containers = {"temp-ecotur-images": d.temp_container, "ecotur-images": d.perm_container}
    service.get_container_client.side_effect = lambda name: containers[name]
    with patch.object(storage_module, "BlobServiceClient", autospec=True) as cls:
        cls.from_connection_string.return_value = service
        d.client = AzureStorageClient()
    return d


def test_init_without_connection_string_raises(monkeypatch):
    """The adapter refuses to start without a connection string."""
    monkeypatch.delenv("AZURE_STORAGE_CONNECTION_STRING", raising=False)

    with pytest.raises(ValueError):
        AzureStorageClient()


async def test_upload_image_rejects_non_image_content_type(doubles):
    """Non-image payloads are rejected with a domain error before any CDN I/O."""
    staged = StagedImage("malware.exe", "application/octet-stream", b"payload")

    with pytest.raises(UnsupportedMediaTypeError):
        await doubles.client.upload_image(staged)

    doubles.source_blob.upload_blob.assert_not_awaited()


async def test_upload_image_happy_path_stores_with_uuid_name(doubles):
    """A valid image is uploaded overwriting, typed, and named <uuid>.<extension>."""
    staged = StagedImage("photo.png", "image/jpeg", b"bytes")

    url = await doubles.client.upload_image(staged)

    assert url == doubles.source_blob.url
    doubles.source_blob.upload_blob.assert_awaited_once()
    args, kwargs = doubles.source_blob.upload_blob.await_args
    assert args == (b"bytes",)
    assert kwargs["overwrite"] is True
    assert kwargs["content_settings"].content_type == "image/jpeg"
    blob_name = doubles.temp_container.get_blob_client.call_args.args[0]
    assert blob_name.endswith(".png")
    assert len(blob_name) == len(".png") + 36


async def test_upload_image_sdk_failure_maps_to_storage_unavailable(doubles):
    """Azure SDK failures surface as StorageUnavailableError chained to the cause."""
    sdk_error = ServiceRequestError("down")
    doubles.source_blob.upload_blob.side_effect = sdk_error

    with pytest.raises(StorageUnavailableError) as exc_info:
        await doubles.client.upload_image(StagedImage("a.jpg", "image/jpeg", b"x"))

    assert exc_info.value.__cause__ is sdk_error


@pytest.mark.parametrize(
    ("url", "is_temporal", "is_permanent"),
    [
        (f"{TEMP_URL}/abc.jpg", True, False),
        (f"{PERM_URL}/abc.jpg", False, True),
        ("https://evil.example/temp-ecotur-images/x.jpg", False, False),
        (f"{TEMP_URL}/nested/abc.jpg", False, False),
        (f"{TEMP_URL}/abc.jpg?sig=1", False, False),
        (f"{TEMP_URL}/", False, False),
        (f"{PERM_URL}/", False, False),
    ],
)
def test_url_classification(doubles, url, is_temporal, is_permanent):
    """Only direct blobs of the account's own containers are classified."""
    assert doubles.client.is_temporal_url(url) is is_temporal
    assert doubles.client.is_permanent_url(url) is is_permanent


async def test_promote_rejects_foreign_url(doubles):
    """A URL outside the temporal container is rejected before copy or delete."""
    with pytest.raises(InvalidImageUrlError):
        await doubles.client.promote_to_permanent("https://evil.example/temp-ecotur-images/x.jpg")

    doubles.dest_blob.start_copy_from_url.assert_not_awaited()
    doubles.source_blob.delete_blob.assert_not_awaited()


async def test_promote_rejects_missing_source_blob(doubles):
    """A temporal URL whose blob no longer exists is rejected without copy or delete."""
    doubles.source_blob.exists.return_value = False

    with pytest.raises(InvalidImageUrlError):
        await doubles.client.promote_to_permanent(f"{TEMP_URL}/abc.jpg")

    doubles.dest_blob.start_copy_from_url.assert_not_awaited()
    doubles.source_blob.delete_blob.assert_not_awaited()


async def test_promote_happy_path_copies_synchronously_then_deletes(doubles):
    """The copy is synchronous and the source is deleted only after it succeeds."""
    url = f"{TEMP_URL}/abc.jpg"

    result = await doubles.client.promote_to_permanent(url)

    assert result == doubles.dest_blob.url
    doubles.dest_blob.start_copy_from_url.assert_awaited_once_with(url, requires_sync=True)
    doubles.source_blob.delete_blob.assert_awaited_once()


async def test_promote_pending_copy_does_not_delete_source(doubles):
    """A copy that is not finished must never cost the source blob (A7)."""
    doubles.dest_blob.start_copy_from_url.return_value = {"copy_status": "pending"}

    with pytest.raises(StorageUnavailableError):
        await doubles.client.promote_to_permanent(f"{TEMP_URL}/abc.jpg")

    doubles.source_blob.delete_blob.assert_not_awaited()


async def test_promote_sdk_failure_does_not_delete_source(doubles):
    """An SDK failure during the copy maps to 503 and keeps the source blob."""
    sdk_error = HttpResponseError("boom")
    doubles.dest_blob.start_copy_from_url.side_effect = sdk_error

    with pytest.raises(StorageUnavailableError) as exc_info:
        await doubles.client.promote_to_permanent(f"{TEMP_URL}/abc.jpg")

    assert exc_info.value.__cause__ is sdk_error
    doubles.source_blob.delete_blob.assert_not_awaited()


async def test_delete_image_deletes_blob_by_name(doubles):
    """delete_image removes the named blob from the permanent container."""
    await doubles.client.delete_image(f"{PERM_URL}/abc.jpg")

    doubles.perm_container.get_blob_client.assert_called_once_with("abc.jpg")
    doubles.dest_blob.delete_blob.assert_awaited_once()


async def test_delete_image_swallows_sdk_failure(doubles):
    """delete_image is best-effort: SDK failures do not propagate."""
    doubles.dest_blob.delete_blob.side_effect = HttpResponseError("boom")

    await doubles.client.delete_image(f"{PERM_URL}/abc.jpg")

    doubles.dest_blob.delete_blob.assert_awaited_once()
