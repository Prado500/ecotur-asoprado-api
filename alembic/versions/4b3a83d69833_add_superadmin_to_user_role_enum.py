"""add_superadmin_to_user_role_enum

Revision ID: 4b3a83d69833
Revises: 22d7d68f4844
Create Date: 2026-08-03 14:40:12.240900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b3a83d69833'
down_revision: Union[str, Sequence[str], None] = '22d7d68f4844'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Injects the 'superadmin' value into the existing PostgreSQL ENUM 'user_role'.
    
    Uses 'IF NOT EXISTS' to ensure idempotency and prevent migration crashes
    if the value was already manually inserted or if the script is re-run.
    """
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'superadmin'")


def downgrade() -> None:
    """
    Reverting ENUM additions in PostgreSQL requires dropping and recreating 
    the entire type, which is an unsafe operation for production data. 
    Therefore, this downgrade is deliberately left as a no-op (pass).
    """
    pass
