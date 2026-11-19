"""users: email_verified_at, filled only by the email-verification link (BE-50)

Revision ID: e50a7c3d9b12
Revises: b51f3c9e2a64
Create Date: 2026-11-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e50a7c3d9b12'
down_revision: Union[str, Sequence[str], None] = 'b51f3c9e2a64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adds users.email_verified_at, NULL in every row, the active ones too (ADR-0022).

    No row is filled: an account active today may have been activated by an admin, and a
    verification nobody saw is not invented. batch_alter_table emits a plain ALTER TABLE on
    PostgreSQL; on SQLite, where the suite runs this function, adding a column needs no rebuild.
    """
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    """Drops users.email_verified_at; SQLite rebuilds the table and keeps its rows."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('email_verified_at')
