"""add branch model

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-09-24 11:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c3d4e5f6g7h8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6g7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    branches_table = op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_branches_name"), "branches", ["name"], unique=True)

    op.bulk_insert(
        branches_table, [{"name": "Main Branch", "location": "Headquarters"}]
    )

    op.add_column("users", sa.Column("branch_id", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            "UPDATE users SET branch_id = (SELECT id FROM branches WHERE name='Main Branch')"
        )
    )
    op.alter_column("users", "branch_id", nullable=False)
    op.create_foreign_key(
        "fk_users_branch_id_branches", "users", "branches", ["branch_id"], ["id"]
    )

    op.add_column("sales", sa.Column("branch_id", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            "UPDATE sales SET branch_id = (SELECT id FROM branches WHERE name='Main Branch')"
        )
    )
    op.alter_column("sales", "branch_id", nullable=False)
    op.create_foreign_key(
        "fk_sales_branch_id_branches", "sales", "branches", ["branch_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_sales_branch_id_branches", "sales", type_="foreignkey")
    op.drop_column("sales", "branch_id")

    op.drop_constraint("fk_users_branch_id_branches", "users", type_="foreignkey")
    op.drop_column("users", "branch_id")

    op.drop_index(op.f("ix_branches_name"), table_name="branches")
    op.drop_table("branches")
