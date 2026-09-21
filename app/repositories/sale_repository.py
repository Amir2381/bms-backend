from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Select, cast, func
from sqlalchemy.orm import Session, joinedload

from app.models.sales import Sale, SaleItem


def create_sale(db: Session, sale: Sale) -> Sale:
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def get_sale(db: Session, sale_id: int) -> Sale | None:
    stmt = (
        Select(Sale)
        .options(
            joinedload(Sale.user),
            joinedload(Sale.items).joinedload(SaleItem.product),
        )
        .where(Sale.id == sale_id)
    )
    return db.scalars(stmt).first()


def get_all_sales(db: Session) -> list[Sale]:
    stmt = Select(Sale).options(
        joinedload(Sale.user),
        joinedload(Sale.items).joinedload(SaleItem.product),
    )
    return list(db.scalars(stmt).unique().all())


def update_sale(db: Session, sale: Sale) -> Sale:
    db.commit()
    db.refresh(sale)
    return sale


def delete_sale(db: Session, sale: Sale) -> None:
    db.delete(sale)
    db.commit()


def get_summary_metrics(db: Session) -> dict:
    sale_totals_subq = (
        Select(
            SaleItem.sale_id,
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("sale_total"),
        )
        .group_by(SaleItem.sale_id)
        .subquery()
    )

    metrics_stmt = Select(
        func.sum(sale_totals_subq.c.sale_total).label("total_sales"),
        func.count(sale_totals_subq.c.sale_id).label("total_transactions"),
        func.avg(sale_totals_subq.c.sale_total).label("average_order_value"),
        func.max(sale_totals_subq.c.sale_total).label("highest_sale"),
        func.min(sale_totals_subq.c.sale_total).label("lowest_sale"),
    )
    metrics_row = db.execute(metrics_stmt).first()

    sold_products_stmt = Select(func.sum(SaleItem.quantity))
    sold_products_count = db.scalar(sold_products_stmt) or 0

    days_stmt = Select(func.count(func.distinct(cast(Sale.sale_date, Date))))
    unique_days = db.scalar(days_stmt) or 1

    total_sales = (
        metrics_row.total_sales
        if metrics_row and metrics_row.total_sales
        else Decimal("0.0")
    )
    total_transactions = (
        metrics_row.total_transactions
        if metrics_row and metrics_row.total_transactions
        else 0
    )
    average_order_value = (
        metrics_row.average_order_value
        if metrics_row and metrics_row.average_order_value
        else Decimal("0.0")
    )

    return {
        "total_sales": Decimal(total_sales),
        "total_transactions": total_transactions,
        "average_order_value": Decimal(average_order_value),
        "highest_sale": (
            Decimal(metrics_row.highest_sale)
            if metrics_row and metrics_row.highest_sale
            else None
        ),
        "lowest_sale": (
            Decimal(metrics_row.lowest_sale)
            if metrics_row and metrics_row.lowest_sale
            else None
        ),
        "average_daily_sales": (
            Decimal(total_sales) / Decimal(unique_days)
            if unique_days > 0
            else Decimal("0.0")
        ),
        "sold_products_count": sold_products_count,
    }


def get_sales_trend(db: Session, period: str = "daily") -> list[dict]:
    stmt = (
        Select(
            cast(Sale.sale_date, Date).label("period"),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("revenue"),
            func.count(func.distinct(Sale.id)).label("transaction_count"),
        )
        .select_from(Sale)
        .join(SaleItem, Sale.id == SaleItem.sale_id)
        .group_by(cast(Sale.sale_date, Date))
        .order_by(cast(Sale.sale_date, Date))
    )

    rows = db.execute(stmt).all()

    return [
        {
            "period": row.period,
            "revenue": Decimal(row.revenue) if row.revenue else Decimal("0.0"),
            "transaction_count": row.transaction_count,
        }
        for row in rows
    ]
