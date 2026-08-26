"""Add status ENVIADO to relatorios_medicao CHECK constraint

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-01-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update CHECK constraint to include ENVIADO status."""
    op.drop_constraint("ck_relatorios_medicao_status", "relatorios_medicao", type_="check")
    op.create_check_constraint(
        "ck_relatorios_medicao_status",
        "relatorios_medicao",
        "status IN ('ATIVO','ENVIADO','EXCLUIDO')",
    )


def downgrade() -> None:
    """Revert CHECK constraint to original ATIVO/EXCLUIDO only."""
    op.drop_constraint("ck_relatorios_medicao_status", "relatorios_medicao", type_="check")
    op.create_check_constraint(
        "ck_relatorios_medicao_status",
        "relatorios_medicao",
        "status IN ('ATIVO','EXCLUIDO')",
    )
