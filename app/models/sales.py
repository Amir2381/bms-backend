from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DDL, ForeignKey, Index, Numeric, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.branch import Branch
    from app.models.customer import Customer
    from app.models.product import Product
    from app.models.user import User


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        Index("ix_sales_branch_date", "branch_id", "sale_date"),
        Index("ix_sales_customer_date", "customer_id", "sale_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    sale_date: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(
        back_populates="sales",
    )
    branch: Mapped["Branch"] = relationship(
        back_populates="sales",
    )
    customer: Mapped["Customer | None"] = relationship(
        back_populates="sales",
    )
    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale",
        cascade="all, delete-orphan",
    )


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    cost_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)

    sale: Mapped["Sale"] = relationship(
        back_populates="items",
    )
    product: Mapped["Product"] = relationship(
        back_populates="sale_items",
    )


create_daily_branch_sales_mv = DDL("""
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
    CREATE UNIQUE INDEX IF NOT EXISTS ix_daily_branch_sales_mv_date_branch
    ON daily_branch_sales_mv (sale_date, branch_id);
    """)

drop_daily_branch_sales_mv = DDL(
    "DROP MATERIALIZED VIEW IF EXISTS daily_branch_sales_mv CASCADE;"
)

event.listen(Base.metadata, "after_create", create_daily_branch_sales_mv)
event.listen(Base.metadata, "before_drop", drop_daily_branch_sales_mv)
