"""feat(auth): agregar campo cedula y estado de activacion (is_active=False) en users

Revision ID: 22d7d68f4844
Revises: c48e057bd4cd
Create Date: 2026-06-15 15:20:35.693163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22d7d68f4844'
down_revision: Union[str, Sequence[str], None] = 'c48e057bd4cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('cedula', sa.String(length=13), nullable=True))
    op.execute("UPDATE users SET cedula = (999000000 + id)::text WHERE cedula IS NULL")
    op.alter_column('users', 'cedula', nullable=False)
    op.create_index(op.f('ix_users_cedula'), 'users', ['cedula'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_cedula'), table_name='users')
    op.drop_column('users', 'cedula')