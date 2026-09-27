from datetime import UTC, datetime

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.sales import Sale, SaleItem
from app.models.system_alert import SystemAlert
from app.repositories import (
    customer_repository,
    product_repository,
    sale_repository,
    user_repository,
)
from app.schemas.sale import SaleCreate
from app.services.exceptions import (
    CustomerNotFoundError,
    InsufficientStockError,
    ProductNotFoundError,
    UserNotFoundError,
)


def check_and_create_alerts(branch_id: int):
    with SessionLocal() as db:
        alerts_data = sale_repository.get_inventory_alerts(
            db, days_threshold=3, lookback_days=30, branch_id=branch_id
        )
        for alert in alerts_data:
            if alert["current_stock"] == 0:
                alert_type = "CRITICAL"
                msg = f"Product '{alert['product_name']}' is out of stock!"
            else:
                alert_type = "WARNING"
                msg = f"Product '{alert['product_name']}' will run out in ~{round(alert['days_remaining'])} days."

            new_alert = SystemAlert(
                branch_id=branch_id,
                type=alert_type,
                message=msg,
            )
            db.add(new_alert)
        db.commit()


def create_sale(
    db: Session,
    sale: SaleCreate,
    background_tasks: BackgroundTasks | None = None,
) -> Sale:
    user = user_repository.get_user(db, sale.user_id)

    if user is None:
        raise UserNotFoundError(sale.user_id)

    if sale.customer_id is not None:
        customer = customer_repository.get_customer(db, sale.customer_id)
        if customer is None:
            raise CustomerNotFoundError(sale.customer_id)

    sale_items = []

    for item in sale.items:
        product = product_repository.get_product(db, item.product_id)

        if product is None:
            raise ProductNotFoundError(item.product_id)

        if product.stock < item.quantity:
            raise InsufficientStockError(
                product_id=product.id,
                requested_quantity=item.quantity,
                available_quantity=product.stock,
            )

        product.stock -= item.quantity

        sale_items.append(
            SaleItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
                cost_price=product.cost_price,
            )
        )

    new_sale = Sale(
        user_id=sale.user_id,
        branch_id=user.branch_id,
        customer_id=sale.customer_id,
        sale_date=datetime.now(UTC),
        created_at=datetime.now(UTC),
        items=sale_items,
    )

    created_sale = sale_repository.create_sale(db, new_sale)

    if background_tasks is not None:
        background_tasks.add_task(check_and_create_alerts, created_sale.branch_id)

    return created_sale
