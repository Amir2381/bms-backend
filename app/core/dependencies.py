from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.repositories import (
    product_repository,
    sale_repository,
    user_repository,
)


def get_product_or_404(product_id: int, db: Session):
    product = product_repository.get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


def get_sale_or_404(sale_id: int, db: Session):
    sale = sale_repository.get_sale(db, sale_id)

    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found",
        )

    return sale


def get_user_or_404(user_id: int, db: Session):
    user = user_repository.get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user
