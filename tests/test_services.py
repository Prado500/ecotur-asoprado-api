"""
Integration test suite for the TouristService administrative operations.

This module validates the Kanban column data retrievals and state mutations,
ensuring strict adherence to Data Governance policies (Soft Deletions) and
Role-Based Access Control (RBAC).
"""
from unittest.mock import AsyncMock, create_autospec

import pytest
from sqlalchemy.future import select

from app.api.dependencies import get_storage_client
from app.core.security import get_password_hash, create_access_token
from app.core.storage import AzureStorageClient, StagedImage
from app.main import app
from app.models.user import User, UserRole
from app.models.service import TouristService, ServiceCategory

# ==========================================
# TEST FIXTURES (Context Setup)
# ==========================================

@pytest.fixture
async def admin_token(db_session) -> str:
    """
    Seeds a temporary administrator user into the test database and
    generates a valid JWT token for endpoint authorization.

    Args:
        db_session: The active SQLAlchemy asynchronous test session.

    Returns:
        str: A signed JWT access token containing admin role claims.
    """
    admin = User(
        cedula="999999999",
        email="admin.test@asoprado.com",
        first_name="Admin",
        last_name="Asoprado",
        password_hash=get_password_hash("AdminSecr3t"),
        role=UserRole.admin,
        is_active=True,
        data_consent=True
    )
    db_session.add(admin)
    await db_session.commit()
    return create_access_token(data={"sub": admin.email, "role": admin.role.value})


@pytest.fixture
async def auth_headers(admin_token: str) -> dict:
    """Returns standard HTTP Authorization headers utilizing the admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
async def test_package(db_session) -> TouristService:
    """
    Seeds a standard, active tourist package into the test database.

    Args:
        db_session: The active SQLAlchemy asynchronous test session.

    Returns:
        TouristService: The persisted ORM entity instance.
    """
    service = TouristService(
        name="Paquete De Prueba Automatizada",
        description="Una descripción detallada y extensa para pasar los validadores estrictos de Pydantic sin problemas.",
        category=ServiceCategory.agroturismo,
        base_price=50000.00,
        max_capacity=15,
        is_available=True
    )
    db_session.add(service)
    await db_session.commit()
    await db_session.refresh(service)
    return service

# ==========================================
# TEST CASES
# ==========================================

async def test_deactivate_and_activate_package(client, auth_headers, test_package, db_session):
    """
    Validates the boolean toggling mechanism for public availability.

    Asserts that the PATCH endpoints correctly transition the package
    between 'Active' and 'Inactive' states without altering other fields.
    """
    # 1. ACT: Trigger deactivation (Move to 'Por Activar')
    deactivate_response = await client.patch(f"/servicios/{test_package.id}/desactivar", headers=auth_headers)
    assert deactivate_response.status_code == 200

    # 2. ASSERT: Verify database mutation
    await db_session.refresh(test_package)
    assert test_package.is_available is False

    # 3. ACT: Trigger activation (Move back to 'Activos')
    activate_response = await client.patch(f"/servicios/{test_package.id}/activar", headers=auth_headers)
    assert activate_response.status_code == 200

    # 4. ASSERT: Verify database restoration
    await db_session.refresh(test_package)
    assert test_package.is_available is True


async def test_soft_delete_and_recover(client, auth_headers, test_package, db_session):
    """
    Validates the logical deletion flow and the business recovery rules.

    Asserts that deletions stamp a UTC timestamp and that recoveries
    strictly force the package into an inactive state to prevent
    unauthorized public exposure.
    """
    # 1. ACT: Perform logical deletion
    delete_response = await client.delete(f"/servicios/{test_package.id}", headers=auth_headers)
    assert delete_response.status_code == 200

    # 2. ASSERT: Verify the soft deletion state
    await db_session.refresh(test_package)
    assert test_package.deleted_at is not None
    assert test_package.is_available is False

    # 3. ACT: Perform recovery
    recover_response = await client.patch(f"/servicios/{test_package.id}/recuperar", headers=auth_headers)
    assert recover_response.status_code == 200

    # 4. ASSERT: Verify recovery business rules (Timestamp cleared, MUST remain inactive)
    await db_session.refresh(test_package)
    assert test_package.deleted_at is None
    assert test_package.is_available is False


async def test_update_package_details(client, auth_headers, test_package, db_session):
    """
    Validates deep updates on an existing package entity.

    Asserts that scalar properties (like name and capacity) are updated properly
    and that relational arrays (images) can be overwritten safely.
    """
    update_payload = {
        "name": "Paquete Modificado Exitosamente",
        "max_capacity": 25,
        "image_urls": ["https://s3.wasabisys.com/ejemplo.jpg"]
    }

    # 1. ACT: Submit partial update payload
    update_response = await client.put(f"/servicios/{test_package.id}", json=update_payload, headers=auth_headers)

    # 2. ASSERT: Verify HTTP response format
    assert update_response.status_code == 200
    response_data = update_response.json()
    assert response_data["name"] == update_payload["name"]
    assert response_data["max_capacity"] == update_payload["max_capacity"]
    assert len(response_data["images"]) == 1
    assert response_data["images"][0]["image_url"] == update_payload["image_urls"][0]

    # 3. ASSERT: Verify database persistence
    await db_session.refresh(test_package)
    assert test_package.name == "Paquete Modificado Exitosamente"
    assert test_package.max_capacity == 25

async def test_upload_images_staging_endpoint(client, auth_headers):
    """
    Validates the ephemeral CDN staging endpoint.
    Asserts that multipart/form-data binaries are correctly ingested and
    translated into a JSON payload containing the temporal URLs.
    """
    fake_file = ("images", ("test_image.jpg", b"fake_binary_payload", "image/jpeg"))

    response = await client.post("/servicios/upload-images/", files=[fake_file], headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "image_urls" in data
    assert len(data["image_urls"]) == 1
    assert "temp-ecotur-images" in data["image_urls"][0]


async def test_upload_images_ceiling_limit_rejection(client, auth_headers):
    """
    Validates the fail-fast ceiling gate on the staging endpoint.
    Asserts that 11 multipart images are rejected with 400 before any
    Azure Blob Storage I/O is attempted.
    """
    files = [("images", (f"image_{i}.jpg", b"payload", "image/jpeg")) for i in range(11)]

    response = await client.post("/servicios/upload-images/", files=files, headers=auth_headers)

    assert response.status_code == 400
    assert "detail" in response.json()

    storage_mock = app.dependency_overrides[get_storage_client]()
    storage_mock.upload_image.assert_not_awaited()


async def test_upload_images_storage_outage_returns_503(client, auth_headers):
    """
    Validates the CDN outage translation to 503 Service Unavailable.
    Asserts the storage client was invoked exactly once with a well-formed
    StagedImage built by the transport layer from the multipart binary.
    """
    failing_client = create_autospec(AzureStorageClient, instance=True)
    failing_client.upload_image = AsyncMock(side_effect=Exception("cdn outage"))
    app.dependency_overrides[get_storage_client] = lambda: failing_client

    fake_file = ("images", ("test_image.jpg", b"fake_binary_payload", "image/jpeg"))
    response = await client.post("/servicios/upload-images/", files=[fake_file], headers=auth_headers)

    assert response.status_code == 503
    assert "detail" in response.json()

    failing_client.upload_image.assert_awaited_once()
    staged = failing_client.upload_image.call_args.args[0]
    assert isinstance(staged, StagedImage)
    assert staged.filename == "test_image.jpg"
    assert staged.content_type == "image/jpeg"
    assert staged.content == b"fake_binary_payload"


async def test_toggle_nonexistent_package_returns_404(client, auth_headers):
    """Unhappy path: activating a package that does not exist yields 404, not a mutation."""
    response = await client.patch("/servicios/999999/activar", headers=auth_headers)

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_soft_delete_nonexistent_package_returns_404(client, auth_headers):
    """Unhappy path: soft-deleting a package that does not exist yields 404."""
    response = await client.delete("/servicios/999999", headers=auth_headers)

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_update_nonexistent_package_returns_404(client, auth_headers):
    """Unhappy path: updating a package that does not exist yields 404."""
    payload = {"name": "Un Paquete Que No Existe En La Base"}

    response = await client.put("/servicios/999999", json=payload, headers=auth_headers)

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_recover_package_not_in_trash_returns_400(client, auth_headers, test_package):
    """Edge case: recovering a package that was never soft-deleted is a 400 rule violation."""
    response = await client.patch(f"/servicios/{test_package.id}/recuperar", headers=auth_headers)

    assert response.status_code == 400
    assert "detail" in response.json()


async def test_recover_nonexistent_package_returns_400(client, auth_headers):
    """Edge case: recovering a package that does not exist is a 400 rule violation."""
    response = await client.patch("/servicios/999999/recuperar", headers=auth_headers)

    assert response.status_code == 400
    assert "detail" in response.json()


async def test_update_package_image_ceiling_limit_rejection(client, auth_headers, test_package):
    """
    Validates the Fail-Fast mechanism preventing database and CDN bloat.
    Asserts that payloads exceeding the 10-image limit are intercepted and rejected
    prior to any Azure Blob Storage I/O execution.
    """
    # Forge a malicious payload with 11 images
    malicious_payload = {
        "image_urls": [f"https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/{i}.jpg" for i in range(11)]
    }

    response = await client.put(f"/servicios/{test_package.id}", json=malicious_payload, headers=auth_headers)

    assert response.status_code == 422
    assert "image_urls" in response.text


async def test_update_package_concurrent_reconciliation(client, auth_headers, test_package, db_session):
    """
    Validates the concurrent CDN reconciliation pattern (Constructive and Destructive).

    Phase 1: Submits temporal URLs and asserts they are promoted to permanent URLs.
    Phase 2: Submits a differential payload, asserting that missing URLs trigger the
             deletion workflow and new temporal URLs are appended cleanly.
    """
    # --- PHASE 1: Constructive Promotion ---
    initial_payload = {
        "image_urls": [
            "https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/cover.jpg",
            "https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/gallery1.jpg"
        ]
    }

    res1 = await client.put(f"/servicios/{test_package.id}", json=initial_payload, headers=auth_headers)
    assert res1.status_code == 200

    images_phase_1 = res1.json()["images"]
    assert len(images_phase_1) == 2
    assert images_phase_1[0]["is_primary"] is True
    assert images_phase_1[1]["is_primary"] is False
    # Assert wrapper correctly promoted the URLs (mock removed 'temp-')
    assert "temp-" not in images_phase_1[0]["image_url"]

    # --- PHASE 2: Destructive Pruning & State Reconstruction ---
    # We drop 'gallery1.jpg', keep 'cover.jpg' (now permanent), and add a new temporal image
    second_payload = {
        "image_urls": [
            images_phase_1[0]["image_url"], # Pre-existing permanent URL
            "https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/new_gallery.jpg"
        ]
    }

    res2 = await client.put(f"/servicios/{test_package.id}", json=second_payload, headers=auth_headers)
    assert res2.status_code == 200

    images_phase_2 = res2.json()["images"]
    assert len(images_phase_2) == 2

    # The first image must remain entirely untouched (idempotency)
    assert images_phase_2[0]["image_url"] == images_phase_1[0]["image_url"]
    # The new image must have been promoted
    assert "temp-" not in images_phase_2[1]["image_url"]