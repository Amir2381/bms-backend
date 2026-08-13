from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_product_or_404,
    get_sale_or_404,
    get_user_or_404,
)
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.sales import Sale, SaleItem
from app.models.user import User
from app.repositories import product_repository, sale_repository
from app.schemas.sale import SaleCreate, SaleResponse

router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


@router.post("", response_model=SaleResponse)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_user_or_404(sale.user_id, db)

    sale_items = []

    for item in sale.items:
        product = get_product_or_404(item.product_id, db)

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.id}",
            )

        product.stock -= item.quantity
        product_repository.update_product(db, product)

        sale_items.append(
            SaleItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
            )
        )

    new_sale = Sale(
        user_id=sale.user_id,
        sale_date=datetime.now(UTC),
        created_at=datetime.now(UTC),
        items=sale_items,
    )

    return sale_repository.create_sale(db, new_sale)


@router.get("", response_model=list[SaleResponse])
def get_all_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_repository.get_all_sales(db)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_sale_or_404(sale_id, db)


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sale = get_sale_or_404(sale_id, db)
    sale_repository.delete_sale(db, sale)

    return {
        "message": "Sale deleted",
    }
