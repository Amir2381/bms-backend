from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.repositories import (
    category_repository,
    product_repository,
    sale_repository,
    user_repository,
)


def get_category_or_404(category_id: int, db: Session):
    category = category_repository.get_category(db, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category


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


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )

    return current_user
