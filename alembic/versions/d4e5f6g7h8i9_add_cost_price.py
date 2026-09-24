"""add cost price

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-09-24 11:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6g7h8i9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6g7h8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "cost_price",
            sa.Numeric(precision=10, scale=2),
            server_default="0.0",
            nullable=False,
        ),
    )
    op.add_column(
        "sale_items",
        sa.Column(
            "cost_price",
            sa.Numeric(precision=10, scale=2),
            server_default="0.0",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("sale_items", "cost_price")
    op.drop_column("products", "cost_price")
