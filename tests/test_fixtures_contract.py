"""Contract tests for the shared doubles and sessions of tests/conftest.py."""

from unittest.mock import MagicMock

import pytest

from app.api.dependencies import get_storage_client
from app.api.routers import user as user_router
from app.core.storage import AzureStorageClient
from app.main import app

CDN_PREFIX = "https://ecoturasopradocdn2026.blob.core.windows.net/"
TEMP = f"{CDN_PREFIX}temp-ecotur-images/a.jpg"
PERM = f"{CDN_PREFIX}ecotur-images/a.jpg"


def test_storage_double_is_specced_on_the_adapter():
    """The global storage double is an instance of the real adapter class."""
    double = app.dependency_overrides[get_storage_client]()

    assert isinstance(double, AzureStorageClient)


def test_storage_double_rejects_unknown_attribute():
    """A method the adapter does not define does not exist on the double."""
    double = app.dependency_overrides[get_storage_client]()

    assert not hasattr(double, "upload_images")


async def test_storage_double_rejects_a_call_off_the_adapter_signature():
    """Awaiting an adapter method with the wrong arguments raises TypeError."""
    double = app.dependency_overrides[get_storage_client]()

    with pytest.raises(TypeError):
        await double.upload_image()


async def test_storage_double_mirrors_the_cdn_url_rules():
    """The double promotes temporary URLs and classifies them like the adapter."""
    double = app.dependency_overrides[get_storage_client]()

    assert await double.promote_to_permanent(TEMP) == PERM
    assert double.is_temporal_url(TEMP) is True
    assert double.is_permanent_url(TEMP) is False
    assert double.is_permanent_url(PERM) is True
    double.promote_to_permanent.assert_awaited_once_with(TEMP)


async def test_email_dispatch_double_is_autouse_and_autospecced(mock_send_email: MagicMock):
    """The router's email dispatch is the autouse double, and it keeps the real signature."""
    assert user_router.send_verification_email is mock_send_email

    with pytest.raises(TypeError):
        await mock_send_email(recipient="x")

    mock_send_email.assert_not_called()
