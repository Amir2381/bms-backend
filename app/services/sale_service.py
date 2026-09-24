from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.sales import Sale, SaleItem
from app.repositories import (
    product_repository,
    sale_repository,
    user_repository,
    customer_repository,
)
from app.schemas.sale import SaleCreate
from app.services.exceptions import (
    InsufficientStockError,
    ProductNotFoundError,
    UserNotFoundError,
    CustomerNotFoundError,
)


def create_sale(db: Session, sale: SaleCreate) -> Sale:
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

    return sale_repository.create_sale(db, new_sale)
