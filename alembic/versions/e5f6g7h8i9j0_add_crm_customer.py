"""add crm customer

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-09-24 11:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e5f6g7h8i9j0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6g7h8i9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customers_phone"), "customers", ["phone"], unique=True)

    op.add_column("sales", sa.Column("customer_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_sales_customer_id_customers", "sales", "customers", ["customer_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_sales_customer_id_customers", "sales", type_="foreignkey")
    op.drop_column("sales", "customer_id")
    op.drop_index(op.f("ix_customers_phone"), table_name="customers")
    op.drop_table("customers")
