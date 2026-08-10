"""add sale timestamps and unit price

Revision ID: 433e0979c4e2
Revises: 4f939975628e
Create Date: 2026-08-10 12:18:59.082257
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "433e0979c4e2"
down_revision: Union[str, Sequence[str], None] = "4f939975628e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("test_table")

    op.add_column(
        "sales",
        sa.Column("unit_price", sa.Float(), nullable=False),
    )
    op.add_column(
        "sales",
        sa.Column("sale_date", sa.DateTime(), nullable=False),
    )
    op.add_column(
        "sales",
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sales", "created_at")
    op.drop_column("sales", "sale_date")
    op.drop_column("sales", "unit_price")

    op.create_table(
        "test_table",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "name",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("test_table_pkey")),
    )
