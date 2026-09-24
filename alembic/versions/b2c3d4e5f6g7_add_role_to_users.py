"""add role to users

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-24 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    userrole = sa.Enum("ADMIN", "SALESPERSON", name="userrole")
    userrole.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column("role", userrole, server_default="SALESPERSON", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
    userrole = sa.Enum("ADMIN", "SALESPERSON", name="userrole")
    userrole.drop(op.get_bind(), checkfirst=True)
