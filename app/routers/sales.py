from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_product_or_404,
    get_sale_or_404,
    get_user_or_404,
    log_request,
)
from app.core.security import get_current_user, get_db
from app.models.sales import Sale
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
    _: None = Depends(log_request),
):
    get_user_or_404(sale.user_id, db)
    product = get_product_or_404(sale.product_id, db)

    if product.stock < sale.quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock",
        )

    product.stock -= sale.quantity
    product_repository.update_product(db, product)

    new_sale = Sale(
        user_id=sale.user_id,
        product_id=sale.product_id,
        quantity=sale.quantity,
    )

    return sale_repository.create_sale(db, new_sale)


@router.get("", response_model=list[SaleResponse])
def get_all_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    return sale_repository.get_all_sales(db)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    return get_sale_or_404(sale_id, db)


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(log_request),
):
    sale = get_sale_or_404(sale_id, db)
    sale_repository.delete_sale(db, sale)

    return {
        "message": "Sale deleted",
    }
