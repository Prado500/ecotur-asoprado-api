"""users: verification_sent_at, when the last verification link was issued (BE-64)

Revision ID: a64d0c2e7f15
Revises: e50a7c3d9b12
Create Date: 2026-11-19 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a64d0c2e7f15'
down_revision: Union[str, Sequence[str], None] = 'e50a7c3d9b12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adds users.verification_sent_at, NULL in every row (ADR-0023).

    No row is filled: the time of a link sent before this column existed was never kept, and an
    empty value lets that account ask for a new link at once, which is what a tourist whose link
    expired needs. batch_alter_table emits a plain ALTER TABLE on PostgreSQL; on SQLite, where
    the suite runs this function, adding a column needs no rebuild.
    """
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column('verification_sent_at', sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    """Drops users.verification_sent_at; SQLite rebuilds the table and keeps its rows."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('verification_sent_at')
