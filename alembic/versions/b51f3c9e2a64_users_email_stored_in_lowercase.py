"""users: every email stored in lowercase (BE-51)

Revision ID: b51f3c9e2a64
Revises: 2cc4b57c136c
Create Date: 2026-11-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b51f3c9e2a64'
down_revision: Union[str, Sequence[str], None] = '2cc4b57c136c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adds CHECK (email = lower(email)) to users: every stored email is lowercase (ADR-0016).

    No row is rewritten. If one already holds an uppercase letter, the database refuses the
    constraint and the migration stops without changing anything, so the CD does not deploy.
    batch_alter_table emits a plain ALTER TABLE on PostgreSQL and rebuilds the table on SQLite,
    which cannot add a constraint in place; the suite runs this function on SQLite.
    """
    with op.batch_alter_table('users') as batch_op:
        batch_op.create_check_constraint('ck_users_email_lowercase', 'email = lower(email)')


def downgrade() -> None:
    """Drops the CHECK; ix_users_email still keeps each email unique."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('ck_users_email_lowercase', type_='check')
