from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def create_product(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_product(db: Session, product_id: int) -> Product | None:
    stmt = select(Product).where(Product.id == product_id)
    product = db.scalars(stmt).first()
    return product


def get_all_products(db: Session) -> list[Product]:
    stmt = select(Product)
    Products = db.scalars(stmt).all()
    return Products


def update_product(db: Session, product: Product) -> Product:
    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
