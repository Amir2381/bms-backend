from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.sales import Sale, SaleItem
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
from app.worker.tasks import check_and_create_alerts


def create_sale(
    db: Session,
    sale: SaleCreate,
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

    check_and_create_alerts.delay(created_sale.branch_id)

    return created_sale
