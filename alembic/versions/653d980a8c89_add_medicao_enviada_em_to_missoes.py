"""Add medicao_enviada_em to missoes table

Revision ID: 653d980a8c89
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "653d980a8c89"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add medicao_enviada_em column to missoes table."""
    op.add_column("missoes", sa.Column("medicao_enviada_em", sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove medicao_enviada_em column from missoes table."""
    op.drop_column("missoes", "medicao_enviada_em")
