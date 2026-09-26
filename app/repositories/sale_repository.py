import datetime
from decimal import Decimal

from sqlalchemy import Date as SqlDate, Numeric
from sqlalchemy import Select, cast, func
from sqlalchemy.orm import Session, aliased, joinedload

from app.models.category import Category
from app.models.customer import Customer
from app.models.product import Product
from app.models.sales import Sale, SaleItem
from app.models.user import User


def create_sale(db: Session, sale: Sale) -> Sale:
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


def get_sale(db: Session, sale_id: int, branch_id: int | None = None) -> Sale | None:
    stmt = (
        Select(Sale)
        .options(
            joinedload(Sale.user),
            joinedload(Sale.items).joinedload(SaleItem.product),
        )
        .where(Sale.id == sale_id)
    )
    if branch_id is not None:
        stmt = stmt.where(Sale.branch_id == branch_id)
    return db.scalars(stmt).first()


def get_all_sales(db: Session, branch_id: int | None = None) -> list[Sale]:
    stmt = Select(Sale).options(
        joinedload(Sale.user),
        joinedload(Sale.items).joinedload(SaleItem.product),
    )
    if branch_id is not None:
        stmt = stmt.where(Sale.branch_id == branch_id)
    return list(db.scalars(stmt).unique().all())


def update_sale(db: Session, sale: Sale) -> Sale:
    db.commit()
    db.refresh(sale)
    return sale


def delete_sale(db: Session, sale: Sale) -> None:
    db.delete(sale)
    db.commit()


def get_summary_metrics(
    db: Session,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    branch_id: int | None = None,
) -> dict:
    sale_totals_stmt = Select(
        SaleItem.sale_id,
        func.sum(SaleItem.quantity * SaleItem.unit_price).label("sale_total"),
        func.sum(SaleItem.quantity * SaleItem.cost_price).label("cost_total"),
    ).select_from(SaleItem)

    if start_date or end_date or branch_id is not None:
        sale_totals_stmt = sale_totals_stmt.join(Sale, Sale.id == SaleItem.sale_id)
        if start_date:
            sale_totals_stmt = sale_totals_stmt.where(
                cast(Sale.sale_date, SqlDate) >= start_date
            )
        if end_date:
            sale_totals_stmt = sale_totals_stmt.where(
                cast(Sale.sale_date, SqlDate) <= end_date
            )
        if branch_id is not None:
            sale_totals_stmt = sale_totals_stmt.where(Sale.branch_id == branch_id)

    sale_totals_subq = sale_totals_stmt.group_by(SaleItem.sale_id).subquery()

    metrics_stmt = Select(
        func.sum(sale_totals_subq.c.sale_total).label("total_sales"),
        func.sum(sale_totals_subq.c.cost_total).label("total_cost"),
        func.count(sale_totals_subq.c.sale_id).label("total_transactions"),
        func.avg(sale_totals_subq.c.sale_total).label("average_order_value"),
        func.max(sale_totals_subq.c.sale_total).label("highest_sale"),
        func.min(sale_totals_subq.c.sale_total).label("lowest_sale"),
    )
    metrics_row = db.execute(metrics_stmt).first()

    sold_products_stmt = Select(func.sum(SaleItem.quantity)).select_from(SaleItem)
    if start_date or end_date or branch_id is not None:
        sold_products_stmt = sold_products_stmt.join(Sale, Sale.id == SaleItem.sale_id)
        if start_date:
            sold_products_stmt = sold_products_stmt.where(
                cast(Sale.sale_date, SqlDate) >= start_date
            )
        if end_date:
            sold_products_stmt = sold_products_stmt.where(
                cast(Sale.sale_date, SqlDate) <= end_date
            )
        if branch_id is not None:
            sold_products_stmt = sold_products_stmt.where(Sale.branch_id == branch_id)

    sold_products_count = db.scalar(sold_products_stmt) or 0

    days_stmt = Select(
        func.count(func.distinct(cast(Sale.sale_date, SqlDate)))
    ).select_from(Sale)
    if start_date:
        days_stmt = days_stmt.where(cast(Sale.sale_date, SqlDate) >= start_date)
    if end_date:
        days_stmt = days_stmt.where(cast(Sale.sale_date, SqlDate) <= end_date)
    if branch_id is not None:
        days_stmt = days_stmt.where(Sale.branch_id == branch_id)

    unique_days = db.scalar(days_stmt) or 1

    unique_customers_stmt = (
        Select(func.count(func.distinct(Sale.customer_id)))
        .select_from(Sale)
        .where(Sale.customer_id.is_not(None))
    )
    if start_date:
        unique_customers_stmt = unique_customers_stmt.where(
            cast(Sale.sale_date, SqlDate) >= start_date
        )
    if end_date:
        unique_customers_stmt = unique_customers_stmt.where(
            cast(Sale.sale_date, SqlDate) <= end_date
        )
    if branch_id is not None:
        unique_customers_stmt = unique_customers_stmt.where(Sale.branch_id == branch_id)

    unique_customers = db.scalar(unique_customers_stmt) or 0

    total_sales = (
        metrics_row.total_sales
        if metrics_row and metrics_row.total_sales
        else Decimal("0.0")
    )
    total_cost = (
        metrics_row.total_cost
        if metrics_row and metrics_row.total_cost
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

    total_profit = Decimal(total_sales) - Decimal(total_cost)
    profit_margin = (
        (total_profit / Decimal(total_sales) * 100)
        if total_sales > 0
        else Decimal("0.0")
    )

    average_clv = (
        (Decimal(total_sales) / Decimal(unique_customers))
        if unique_customers > 0
        else Decimal("0.0")
    )

    return {
        "total_sales": Decimal(total_sales),
        "total_profit": total_profit,
        "profit_margin": round(profit_margin, 2),
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
        "average_clv": round(average_clv, 2),
    }


def get_sales_trend(
    db: Session,
    period: str = "daily",
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    branch_id: int | None = None,
) -> list[dict]:
    stmt = (
        Select(
            cast(Sale.sale_date, SqlDate).label("period"),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("revenue"),
            func.count(func.distinct(Sale.id)).label("transaction_count"),
        )
        .select_from(Sale)
        .join(SaleItem, Sale.id == SaleItem.sale_id)
    )

    if start_date:
        stmt = stmt.where(cast(Sale.sale_date, SqlDate) >= start_date)
    if end_date:
        stmt = stmt.where(cast(Sale.sale_date, SqlDate) <= end_date)
    if branch_id is not None:
        stmt = stmt.where(Sale.branch_id == branch_id)

    stmt = stmt.group_by(cast(Sale.sale_date, SqlDate)).order_by(
        cast(Sale.sale_date, SqlDate)
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


def get_product_performance(
    db: Session,
    limit: int = 10,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    branch_id: int | None = None,
) -> list[dict]:
    total_revenue_stmt = Select(
        func.sum(SaleItem.quantity * SaleItem.unit_price)
    ).select_from(SaleItem)

    if start_date or end_date or branch_id is not None:
        total_revenue_stmt = total_revenue_stmt.join(Sale, Sale.id == SaleItem.sale_id)
        if start_date:
            total_revenue_stmt = total_revenue_stmt.where(
                cast(Sale.sale_date, SqlDate) >= start_date
            )
        if end_date:
            total_revenue_stmt = total_revenue_stmt.where(
                cast(Sale.sale_date, SqlDate) <= end_date
            )
        if branch_id is not None:
            total_revenue_stmt = total_revenue_stmt.where(Sale.branch_id == branch_id)

    total_revenue = db.scalar(total_revenue_stmt) or Decimal("0.0")

    stmt = (
        Select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.sum(SaleItem.quantity).label("quantity_sold"),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("revenue"),
        )
        .select_from(SaleItem)
        .join(Product, Product.id == SaleItem.product_id)
    )

    if start_date or end_date or branch_id is not None:
        stmt = stmt.join(Sale, Sale.id == SaleItem.sale_id)
        if start_date:
            stmt = stmt.where(cast(Sale.sale_date, SqlDate) >= start_date)
        if end_date:
            stmt = stmt.where(cast(Sale.sale_date, SqlDate) <= end_date)
        if branch_id is not None:
            stmt = stmt.where(Sale.branch_id == branch_id)

    stmt = (
        stmt.group_by(Product.id, Product.name)
        .order_by(func.sum(SaleItem.quantity * SaleItem.unit_price).desc())
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity_sold": row.quantity_sold,
            "revenue": Decimal(row.revenue),
            "revenue_share": (
                round((Decimal(row.revenue) / Decimal(total_revenue)) * 100, 2)
                if total_revenue > 0
                else Decimal("0.0")
            ),
        }
        for row in rows
    ]


def get_category_performance(
    db: Session,
    limit: int = 10,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    branch_id: int | None = None,
) -> list[dict]:
    total_revenue_stmt = Select(
        func.sum(SaleItem.quantity * SaleItem.unit_price)
    ).select_from(SaleItem)

    if start_date or end_date or branch_id is not None:
        total_revenue_stmt = total_revenue_stmt.join(Sale, Sale.id == SaleItem.sale_id)
        if start_date:
            total_revenue_stmt = total_revenue_stmt.where(
                cast(Sale.sale_date, SqlDate) >= start_date
            )
        if end_date:
            total_revenue_stmt = total_revenue_stmt.where(
                cast(Sale.sale_date, SqlDate) <= end_date
            )
        if branch_id is not None:
            total_revenue_stmt = total_revenue_stmt.where(Sale.branch_id == branch_id)

    total_revenue = db.scalar(total_revenue_stmt) or Decimal("0.0")

    stmt = (
        Select(
            Category.id.label("category_id"),
            func.coalesce(Category.name, "Uncategorized").label("category_name"),
            func.sum(SaleItem.quantity).label("quantity_sold"),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("revenue"),
        )
        .select_from(SaleItem)
        .join(Product, Product.id == SaleItem.product_id)
        .outerjoin(Category, Category.id == Product.category_id)
    )

    if start_date or end_date or branch_id is not None:
        stmt = stmt.join(Sale, Sale.id == SaleItem.sale_id)
        if start_date:
            stmt = stmt.where(cast(Sale.sale_date, SqlDate) >= start_date)
        if end_date:
            stmt = stmt.where(cast(Sale.sale_date, SqlDate) <= end_date)
        if branch_id is not None:
            stmt = stmt.where(Sale.branch_id == branch_id)

    stmt = (
        stmt.group_by(Category.id, Category.name)
        .order_by(func.sum(SaleItem.quantity * SaleItem.unit_price).desc())
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    return [
        {
            "category_id": row.category_id,
            "category_name": row.category_name,
            "quantity_sold": row.quantity_sold,
            "revenue": Decimal(row.revenue),
            "revenue_share": (
                round((Decimal(row.revenue) / Decimal(total_revenue)) * 100, 2)
                if total_revenue > 0
                else Decimal("0.0")
            ),
        }
        for row in rows
    ]


def get_salesperson_performance(
    db: Session,
    limit: int = 10,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    branch_id: int | None = None,
) -> list[dict]:
    stmt = (
        Select(
            User.id.label("user_id"),
            User.full_name.label("user_name"),
            func.sum(SaleItem.quantity).label("quantity_sold"),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("revenue"),
            func.count(func.distinct(Sale.id)).label("transaction_count"),
        )
        .select_from(SaleItem)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .join(User, User.id == Sale.user_id)
    )

    if start_date:
        stmt = stmt.where(cast(Sale.sale_date, SqlDate) >= start_date)
    if end_date:
        stmt = stmt.where(cast(Sale.sale_date, SqlDate) <= end_date)
    if branch_id is not None:
        stmt = stmt.where(Sale.branch_id == branch_id)

    stmt = (
        stmt.group_by(User.id, User.full_name)
        .order_by(func.sum(SaleItem.quantity * SaleItem.unit_price).desc())
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    return [
        {
            "user_id": row.user_id,
            "user_name": row.user_name,
            "quantity_sold": row.quantity_sold or 0,
            "revenue": Decimal(row.revenue) if row.revenue else Decimal("0.0"),
            "transaction_count": row.transaction_count or 0,
        }
        for row in rows
    ]


def get_top_customers(
    db: Session,
    limit: int = 10,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    branch_id: int | None = None,
) -> list[dict]:
    profit_expression = SaleItem.quantity * (SaleItem.unit_price - SaleItem.cost_price)

    stmt = (
        Select(
            Customer.id.label("customer_id"),
            Customer.full_name.label("customer_name"),
            Customer.phone.label("customer_phone"),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("revenue"),
            func.sum(profit_expression).label("profit"),
            func.count(func.distinct(Sale.id)).label("transaction_count"),
        )
        .select_from(SaleItem)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .join(Customer, Customer.id == Sale.customer_id)
    )

    if start_date:
        stmt = stmt.where(cast(Sale.sale_date, SqlDate) >= start_date)
    if end_date:
        stmt = stmt.where(cast(Sale.sale_date, SqlDate) <= end_date)
    if branch_id is not None:
        stmt = stmt.where(Sale.branch_id == branch_id)

    stmt = (
        stmt.group_by(Customer.id, Customer.full_name, Customer.phone)
        .order_by(func.sum(profit_expression).desc())
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "revenue": Decimal(row.revenue) if row.revenue else Decimal("0.0"),
            "profit": Decimal(row.profit) if row.profit else Decimal("0.0"),
            "transaction_count": row.transaction_count or 0,
        }
        for row in rows
    ]


def get_cross_selling_products(
    db: Session,
    limit_per_product: int = 3,
    product_id: int | None = None,
    branch_id: int | None = None,
) -> list[dict]:
    si1 = aliased(SaleItem)
    si2 = aliased(SaleItem)
    p1 = aliased(Product)
    p2 = aliased(Product)

    stmt = (
        Select(
            si1.product_id.label("product_id"),
            p1.name.label("product_name"),
            si2.product_id.label("recommended_product_id"),
            p2.name.label("recommended_product_name"),
            func.count(si1.sale_id).label("frequency"),
        )
        .select_from(si1)
        .join(si2, si1.sale_id == si2.sale_id)
        .join(p1, si1.product_id == p1.id)
        .join(p2, si2.product_id == p2.id)
        .where(si1.product_id != si2.product_id)
    )

    if product_id is not None:
        stmt = stmt.where(si1.product_id == product_id)
    if branch_id is not None:
        stmt = stmt.join(Sale, Sale.id == si1.sale_id).where(
            Sale.branch_id == branch_id
        )

    stmt = stmt.group_by(si1.product_id, p1.name, si2.product_id, p2.name).order_by(
        si1.product_id, func.count(si1.sale_id).desc()
    )

    rows = db.execute(stmt).all()

    results = {}
    for row in rows:
        pid = row.product_id
        if pid not in results:
            results[pid] = {
                "product_id": pid,
                "product_name": row.product_name,
                "recommendations": [],
            }
        if len(results[pid]["recommendations"]) < limit_per_product:
            results[pid]["recommendations"].append(
                {
                    "product_id": row.recommended_product_id,
                    "product_name": row.recommended_product_name,
                    "frequency": row.frequency,
                }
            )

    return list(results.values())


def get_inventory_alerts(
    db: Session,
    days_threshold: int = 7,
    lookback_days: int = 30,
    branch_id: int | None = None,
) -> list[dict]:
    lookback_date = datetime.datetime.now(
        datetime.timezone.utc
    ).date() - datetime.timedelta(days=lookback_days)

    sales_subq_stmt = (
        Select(SaleItem.product_id, func.sum(SaleItem.quantity).label("total_sold"))
        .join(Sale, Sale.id == SaleItem.sale_id)
        .where(cast(Sale.sale_date, SqlDate) >= lookback_date)
    )

    if branch_id is not None:
        sales_subq_stmt = sales_subq_stmt.where(Sale.branch_id == branch_id)

    sales_subq = sales_subq_stmt.group_by(SaleItem.product_id).subquery()

    daily_run_rate = cast(sales_subq.c.total_sold, Numeric(10, 4)) / lookback_days

    days_remaining = cast(Product.stock, Numeric(10, 4)) / func.nullif(
        daily_run_rate, 0
    )

    stmt = (
        Select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.stock.label("current_stock"),
            func.coalesce(daily_run_rate, 0).label("daily_run_rate"),
            days_remaining.label("days_remaining"),
        )
        .select_from(Product)
        .join(sales_subq, Product.id == sales_subq.c.product_id)
        .where((days_remaining <= days_threshold) | (Product.stock == 0))
        .order_by(days_remaining.asc().nulls_last())
    )

    rows = db.execute(stmt).all()

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "current_stock": row.current_stock,
            "daily_run_rate": (
                Decimal(row.daily_run_rate)
                if row.daily_run_rate is not None
                else Decimal("0.0")
            ),
            "days_remaining": (
                Decimal(row.days_remaining) if row.days_remaining is not None else None
            ),
        }
        for row in rows
    ]
