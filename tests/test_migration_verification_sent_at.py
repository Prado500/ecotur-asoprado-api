"""Tests for the BE-64 migration: users.verification_sent_at is born empty (ADR-0023).

The migration runs on a SQLite database of its own, as the one of ADR-0022 does in
test_migration_email_verified_at.py: the accounts are written with the full schema, the downgrade
removes the column and the upgrade adds it back, so the test reads what the upgrade leaves in
existing rows. Empty means that no link is on record: the account may ask for one at once.
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
from app.models.user import UserRole

COLUMN = "verification_sent_at"
MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "a64d0c2e7f15_users_verification_sent_at.py"
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

    A pending tourist, a verified tourist and an admin: the upgrade invents a send for none.
    """
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        Base.metadata.create_all(connection)
        connection.commit()
        with Session(connection) as session:
            session.add_all(
                [
                    make_user(is_active=False),
                    make_user(is_active=True, email_verified_at=datetime.now(UTC)),
                    make_user(role=UserRole.admin, is_active=True),
                ]
            )
            session.commit()
        _migrate(connection, "downgrade")
        connection.commit()
        yield connection
    engine.dispose()


def test_migration_adds_the_column_empty_in_every_row(pre_migration_db: Connection) -> None:
    """Happy path: the column comes back nullable and NULL in every row."""
    assert COLUMN not in _columns(pre_migration_db)

    _migrate(pre_migration_db, "upgrade")

    assert _columns(pre_migration_db)[COLUMN] is True
    rows = pre_migration_db.execute(text("SELECT verification_sent_at FROM users")).all()
    assert [sent_at for (sent_at,) in rows] == [None, None, None]


def test_migration_downgrade_drops_only_its_column_and_keeps_the_rows(
    pre_migration_db: Connection,
) -> None:
    """Edge case: a filled send time goes away with its column; rows and verified mark stay."""
    _migrate(pre_migration_db, "upgrade")
    pre_migration_db.execute(text("UPDATE users SET verification_sent_at = CURRENT_TIMESTAMP"))

    _migrate(pre_migration_db, "downgrade")

    assert COLUMN not in _columns(pre_migration_db)
    assert "email_verified_at" in _columns(pre_migration_db)
    verified = "SELECT count(*) FROM users WHERE email_verified_at IS NOT NULL"
    assert pre_migration_db.execute(text(verified)).scalar_one() == 1
    assert pre_migration_db.execute(text("SELECT count(*) FROM users")).scalar_one() == 3
