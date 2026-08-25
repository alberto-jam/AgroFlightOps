"""Add relatorios_medicao and relatorio_medicao_missoes tables

Revision ID: a1b2c3d4e5f6
Revises: 653d980a8c89
Create Date: 2025-01-15 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "653d980a8c89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create relatorios_medicao and relatorio_medicao_missoes tables."""
    op.create_table(
        "relatorios_medicao",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.BigInteger(), nullable=False),
        sa.Column("s3_key", sa.String(500), nullable=False),
        sa.Column("data_inicial", sa.Date(), nullable=False),
        sa.Column("data_final", sa.Date(), nullable=False),
        sa.Column("total_area", sa.Numeric(14, 2), nullable=False),
        sa.Column("qtd_missoes", sa.Integer(), nullable=False),
        sa.Column(
            "gerado_em",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("gerado_por", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'ATIVO'"),
        ),
        sa.Column("enviado_em", sa.DateTime(), nullable=True),
        sa.Column("enviado_para", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
            name="fk_relatorios_medicao_cliente",
        ),
        sa.ForeignKeyConstraint(
            ["gerado_por"],
            ["usuarios.id"],
            name="fk_relatorios_medicao_gerador",
        ),
        sa.CheckConstraint(
            "status IN ('ATIVO', 'EXCLUIDO')",
            name="ck_relatorios_medicao_status",
        ),
        sa.CheckConstraint(
            "total_area >= 0",
            name="ck_relatorios_medicao_total_area",
        ),
        sa.CheckConstraint(
            "qtd_missoes > 0",
            name="ck_relatorios_medicao_qtd_missoes",
        ),
    )

    op.create_table(
        "relatorio_medicao_missoes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("relatorio_id", sa.BigInteger(), nullable=False),
        sa.Column("missao_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["relatorio_id"],
            ["relatorios_medicao.id"],
            name="fk_relatorio_missoes_relatorio",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["missao_id"],
            ["missoes.id"],
            name="fk_relatorio_missoes_missao",
        ),
        sa.UniqueConstraint(
            "relatorio_id",
            "missao_id",
            name="uq_relatorio_medicao_missoes",
        ),
    )


def downgrade() -> None:
    """Drop relatorio_medicao_missoes and relatorios_medicao tables."""
    op.drop_table("relatorio_medicao_missoes")
    op.drop_table("relatorios_medicao")
