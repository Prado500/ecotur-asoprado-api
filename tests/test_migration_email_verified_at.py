"""Tests for the BE-50 migration: users.email_verified_at is born empty in every row (ADR-0022).

The migration runs on a SQLite database of its own, as the one of ADR-0016 does in
test_email_case.py: the accounts are written with the full schema, the downgrade removes the
column and the upgrade adds it back, so the test reads what the upgrade leaves in existing rows.
"""

import runpy
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Connection, create_engine, inspect, text
from sqlalchemy.orm import Session

from app.db.database import Base

COLUMN = "email_verified_at"
MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "e50a7c3d9b12_users_email_verified_at.py"
)


def _migrate(connection: Connection, step: str) -> None:
    """Runs upgrade() or downgrade() of the migration under test, with its own op."""
    migration = runpy.run_path(str(MIGRATION))
    with Operations.context(MigrationContext.configure(connection)):
        migration[step]()


def _columns(connection: Connection) -> dict[str, bool]:
    """Maps each column of users to whether it admits NULL."""
    columns = inspect(connection).get_columns("users")
    return {column["name"]: column["nullable"] for column in columns}


@pytest.fixture
def pre_migration_db(make_user) -> Iterator[Connection]:
    """A SQLite database of its own with three accounts, on the schema before the migration.

    One account is active, one inactive and one soft-deleted: the upgrade must not read a
    verification into any of them.
    """
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        Base.metadata.create_all(connection)
        connection.commit()
        with Session(connection) as session:
            session.add_all(
                [
                    make_user(is_active=True),
                    make_user(is_active=False),
                    make_user(is_active=False, deleted_at=datetime.now(UTC)),
                ]
            )
            session.commit()
        _migrate(connection, "downgrade")
        connection.commit()
        yield connection
    engine.dispose()


def test_migration_adds_the_column_empty_in_every_row(pre_migration_db: Connection) -> None:
    """Happy path: the column comes back nullable and NULL in every row, the active one too."""
    assert COLUMN not in _columns(pre_migration_db)

    _migrate(pre_migration_db, "upgrade")

    assert _columns(pre_migration_db)[COLUMN] is True
    rows = pre_migration_db.execute(text("SELECT is_active, email_verified_at FROM users")).all()
    assert sorted(is_active for is_active, _ in rows) == [False, False, True]
    assert [verified_at for _, verified_at in rows] == [None, None, None]


def test_migration_downgrade_drops_the_column_and_keeps_the_rows(
    pre_migration_db: Connection,
) -> None:
    """Edge case: a filled mark goes away with its column; the three accounts stay."""
    _migrate(pre_migration_db, "upgrade")
    pre_migration_db.execute(text("UPDATE users SET email_verified_at = CURRENT_TIMESTAMP"))

    _migrate(pre_migration_db, "downgrade")

    assert COLUMN not in _columns(pre_migration_db)
    assert pre_migration_db.execute(text("SELECT count(*) FROM users")).scalar_one() == 3
