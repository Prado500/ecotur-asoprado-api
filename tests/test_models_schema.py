"""Characterization test: freezes the database schema declared by ``app.models``.

The expected values below are literals on purpose. Deriving them from ``Base.metadata`` or from
the Alembic migrations at run time would make the test agree with itself. Every column type is
compiled for the PostgreSQL dialect, so ENUM names, JSONB and NUMERIC(10, 2) are compared as
PostgreSQL sees them and not as SQLite does.
"""

from typing import Any, NamedTuple

import pytest
from sqlalchemy import Column, ColumnDefault, DefaultClause, Enum, inspect
from sqlalchemy.dialects import postgresql

import app.models  # noqa: F401  # registers the four tables on Base.metadata
from app.db.database import Base
from app.models.service import ServiceCategory, ServiceImage, TouristService
from app.models.user import UserRole

PG = postgresql.dialect()

TZ = "TIMESTAMP WITH TIME ZONE"


class FrozenColumn(NamedTuple):
    """Normalized, comparable description of one declared column."""

    sql_type: str
    nullable: bool = False
    primary_key: bool = False
    indexed: bool = False
    unique: bool = False
    server_default: str | None = None
    default: object = None
    foreign_key: tuple[str, str | None] | None = None


def _describe(column: Column[Any]) -> FrozenColumn:
    """Reduce a declared column to the schema facts that must not drift.

    Args:
        column: Column taken from ``Base.metadata``.

    Returns:
        The frozen description, with the type compiled for PostgreSQL.
    """
    server_default = column.server_default
    default = column.default
    foreign_key = next(iter(column.foreign_keys), None)
    return FrozenColumn(
        sql_type=column.type.compile(dialect=PG),
        nullable=bool(column.nullable),
        primary_key=column.primary_key,
        indexed=bool(column.index),
        unique=bool(column.unique),
        server_default=(
            str(server_default.arg) if isinstance(server_default, DefaultClause) else None
        ),
        default=default.arg if isinstance(default, ColumnDefault) else None,
        foreign_key=(
            (foreign_key.target_fullname, foreign_key.ondelete) if foreign_key is not None else None
        ),
    )


EXPECTED: dict[str, dict[str, FrozenColumn]] = {
    "users": {
        "id": FrozenColumn("INTEGER", primary_key=True, indexed=True),
        "cedula": FrozenColumn("VARCHAR(13)", indexed=True, unique=True),
        "email": FrozenColumn("VARCHAR(150)", indexed=True, unique=True),
        "password_hash": FrozenColumn("VARCHAR(255)"),
        "first_name": FrozenColumn("VARCHAR(100)"),
        "last_name": FrozenColumn("VARCHAR(100)"),
        "phone": FrozenColumn("VARCHAR(20)", nullable=True),
        "role": FrozenColumn("user_role", default=UserRole.tourist),
        "data_consent": FrozenColumn("BOOLEAN", default=False),
        "is_active": FrozenColumn("BOOLEAN", default=False),
        "created_at": FrozenColumn(TZ, nullable=True, server_default="now()"),
        "deleted_at": FrozenColumn(TZ, nullable=True),
    },
    "tourist_services": {
        "id": FrozenColumn("INTEGER", primary_key=True, indexed=True),
        "name": FrozenColumn("VARCHAR(150)"),
        "description": FrozenColumn("TEXT", nullable=True),
        "category": FrozenColumn("servicecategory", default=ServiceCategory.otro),
        "base_price": FrozenColumn("NUMERIC(10, 2)"),
        "max_capacity": FrozenColumn("INTEGER"),
        "is_available": FrozenColumn("BOOLEAN", default=False),
        "created_at": FrozenColumn(TZ, nullable=True, server_default="now()"),
        "deleted_at": FrozenColumn(TZ, nullable=True),
    },
    "service_images": {
        "id": FrozenColumn("INTEGER", primary_key=True, indexed=True),
        "service_id": FrozenColumn("INTEGER", foreign_key=("tourist_services.id", "CASCADE")),
        "image_url": FrozenColumn("TEXT"),
        "is_primary": FrozenColumn("BOOLEAN", nullable=True, default=False),
        "created_at": FrozenColumn(TZ, nullable=True, server_default="now()"),
    },
    "audit_logs": {
        "id": FrozenColumn("INTEGER", primary_key=True, indexed=True),
        "entity_name": FrozenColumn("VARCHAR(50)", indexed=True),
        "entity_id": FrozenColumn("VARCHAR(50)", indexed=True),
        "action": FrozenColumn("audit_action_enum"),
        "changes": FrozenColumn("JSONB", nullable=True),
        "performed_by": FrozenColumn("VARCHAR(50)", indexed=True),
        "timestamp": FrozenColumn(TZ, nullable=True, server_default="now()", indexed=True),
    },
}

EXPECTED_ENUMS: dict[str, list[str]] = {
    "user_role": ["superadmin", "admin", "tourist"],
    "servicecategory": ["agroturismo", "recreacional", "metalmecanico", "otro"],
    "audit_action_enum": ["CREATE", "UPDATE", "SOFT_DELETE", "RECOVER", "ACTIVATE", "DEACTIVATE"],
}


def test_metadata_holds_exactly_the_frozen_tables() -> None:
    assert set(Base.metadata.tables) == set(EXPECTED)


@pytest.mark.parametrize("table_name", sorted(EXPECTED))
def test_table_columns_match_the_frozen_schema(table_name: str) -> None:
    table = Base.metadata.tables[table_name]

    described = {column.name: _describe(column) for column in table.columns}

    assert described == EXPECTED[table_name]


def test_enum_types_keep_their_postgres_names_and_labels() -> None:
    found: dict[str, list[str]] = {}
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, Enum) and column.type.name is not None:
                found[column.type.name] = list(column.type.enums)

    assert found == EXPECTED_ENUMS


def test_service_relationships_keep_target_direction_and_cascade() -> None:
    images = inspect(TouristService).relationships["images"]
    service = inspect(ServiceImage).relationships["service"]

    assert images.mapper.class_ is ServiceImage
    assert images.uselist is True
    assert images.back_populates == "service"
    assert set(images.cascade) == {
        "save-update",
        "merge",
        "refresh-expire",
        "expunge",
        "delete",
        "delete-orphan",
    }
    assert service.mapper.class_ is TouristService
    assert service.uselist is False
    assert service.back_populates == "images"
    assert set(service.cascade) == {"save-update", "merge"}
