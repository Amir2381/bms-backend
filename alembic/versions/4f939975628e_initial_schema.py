"""initial schema

Revision ID: 4f939975628e
Revises:
Create Date: 2026-08-09 16:38:30.251732

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "4f939975628e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
