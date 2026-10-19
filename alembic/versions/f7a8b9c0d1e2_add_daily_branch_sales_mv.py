from typing import Sequence, Union

from alembic import op

revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "412a2ceba298"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS daily_branch_sales_mv AS
        SELECT
            CAST(s.sale_date AS DATE) AS sale_date,
            s.branch_id AS branch_id,
            COALESCE(SUM(si.quantity * si.unit_price), 0) AS total_revenue,
            COALESCE(SUM(si.quantity * (si.unit_price - si.cost_price)), 0) AS total_profit,
            COUNT(DISTINCT s.id) AS transaction_count
        FROM sales s
        JOIN sale_items si ON s.id = si.sale_id
        GROUP BY CAST(s.sale_date AS DATE), s.branch_id;
        """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_daily_branch_sales_mv_date_branch
        ON daily_branch_sales_mv (sale_date, branch_id);
        """)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS daily_branch_sales_mv CASCADE;")
