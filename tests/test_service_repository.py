"""
Repository test suite for ServiceRepository.save_service.

Runs against the real repository and a real session: save_service's contract is what
it does with the row in the database, and that cannot be observed through a double.
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import ServiceCategory, ServiceImage, TouristService
from app.repositories.service_repository import ServiceRepository


@pytest.fixture
def repo(db_session: AsyncSession) -> ServiceRepository:
    """Builds the repository under test on the test's own session."""
    return ServiceRepository(db_session)


def _package(**overrides: Any) -> TouristService:
    """Builds a transient package with valid defaults, not attached to any session."""
    values: dict[str, Any] = {
        "name": "Paquete De Prueba Automatizada",
        "base_price": Decimal("50000.00"),
        "max_capacity": 15,
        "category": ServiceCategory.agroturismo,
        "is_available": True,
    }
    values.update(overrides)
    return TouristService(**values)


async def _persist(db_session: AsyncSession, package: TouristService) -> TouristService:
    """Commits a package and reloads its columns, leaving its images unloaded."""
    db_session.add(package)
    await db_session.commit()
    await db_session.refresh(package, attribute_names=["id", "deleted_at", "is_available"])
    return package


async def test_save_service_commits_pending_changes_and_returns_the_row(
    db_session: AsyncSession, repo: ServiceRepository
) -> None:
    """The pending change survives a later rollback, and the row returned is this id's of two."""
    package = await _persist(db_session, _package())
    await _persist(db_session, _package(name="Paquete Vecino De Prueba"))
    package.is_available = False

    saved = await repo.save_service(package)
    await db_session.rollback()
    await db_session.refresh(saved)

    assert saved.id == package.id
    assert saved.is_available is False


async def test_save_service_raises_when_the_row_never_existed(
    repo: ServiceRepository,
) -> None:
    """A row that was never inserted breaks the invariant, so there is nothing to return."""
    with pytest.raises(NoResultFound):
        await repo.save_service(_package(id=999_999))


async def test_save_service_raises_when_the_row_was_physically_deleted(
    db_session: AsyncSession, repo: ServiceRepository
) -> None:
    """A row deleted from the table before the call raises instead of returning None."""
    package = await _persist(db_session, _package())
    await db_session.execute(delete(TouristService).where(TouristService.id == package.id))
    await db_session.commit()

    with pytest.raises(NoResultFound):
        await repo.save_service(package)


async def test_save_service_returns_a_soft_deleted_row(
    db_session: AsyncSession, repo: ServiceRepository
) -> None:
    """A soft-deleted row still exists, so saving it returns it with its own deletion date."""
    deleted_at = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    package = await _persist(db_session, _package(deleted_at=deleted_at))
    await _persist(db_session, _package(name="Paquete Vecino De Prueba"))

    saved = await repo.save_service(package)

    assert saved.id == package.id
    # SQLite returns the column without its time zone.
    assert saved.deleted_at == deleted_at.replace(tzinfo=None)


async def test_save_service_returns_the_row_with_its_images_loaded(
    db_session: AsyncSession, repo: ServiceRepository
) -> None:
    """Images read after the call need no lazy load, which would raise MissingGreenlet."""
    image_url = "https://cdn.example.test/ecotur-images/package.jpg"
    package = await _persist(db_session, _package())
    db_session.add(ServiceImage(service_id=package.id, image_url=image_url))
    await db_session.commit()

    saved = await repo.save_service(package)

    assert [image.image_url for image in saved.images] == [image_url]
