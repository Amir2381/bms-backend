"""add category model

Revision ID: a1b2c3d4e5f6
Revises: 4f939975628e
Create Date: 2026-09-21 16:50:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "4f939975628e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)
    op.add_column("products", sa.Column("category_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_products_category_id_categories",
        "products",
        "categories",
        ["category_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_products_category_id_categories", "products", type_="foreignkey"
    )
    op.drop_column("products", "category_id")
    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_table("categories")
