"""Contract tests for the shared doubles and sessions of tests/conftest.py."""

from typing import Any

import pytest
from sqlalchemy import func, select

from app.api.dependencies import get_storage_client
from app.api.routers import user as user_router
from app.core.email import send_verification_email as real_send_verification_email
from app.core.storage import AzureStorageClient
from app.db.database import get_db
from app.main import app
from app.models.user import User

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


async def test_email_dispatch_double_is_autouse_and_autospecced(mock_send_email: Any):
    """The router's email dispatch is the autouse double, and it keeps the real signature."""
    double: Any = user_router.send_verification_email
    assert double is mock_send_email

    with pytest.raises(TypeError):
        await double(recipient="x")

    double.assert_not_called()


def test_email_dispatch_is_patched_without_requesting_the_fixture():
    """The autouse email double is active in a test that does not request it."""
    assert user_router.send_verification_email is not real_send_verification_email


async def test_each_request_gets_its_own_session(client, db_session):
    """Each request receives a fresh app session, never the test's own session."""
    first_request = app.dependency_overrides[get_db]()
    second_request = app.dependency_overrides[get_db]()

    first_session = await anext(first_request)
    second_session = await anext(second_request)
    await second_request.aclose()
    await first_request.aclose()

    assert first_session is not db_session
    assert second_session is not first_session


async def test_app_flush_without_commit_is_invisible_to_the_test(client, db_session, make_user):
    """A row the app flushes but never commits is gone once its session closes."""
    request = app.dependency_overrides[get_db]()
    app_session = await anext(request)

    app_session.add(make_user())
    await app_session.flush()
    await request.aclose()

    count = await db_session.scalar(select(func.count()).select_from(User))
    assert count == 0


async def test_app_commit_is_visible_to_the_test(client, db_session, make_user):
    """A row the app commits is visible to the test's session."""
    user = make_user()
    request = app.dependency_overrides[get_db]()
    app_session = await anext(request)

    app_session.add(user)
    await app_session.commit()
    await request.aclose()

    result = await db_session.execute(select(User).where(User.cedula == user.cedula))
    rows = result.scalars().all()
    assert [row.email for row in rows] == [user.email]
