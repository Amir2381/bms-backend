from sqlalchemy import func, select
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


def get_all_products(
    db: Session,
    name: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    in_stock: bool | None = None,
    sort: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Product], int]:
    stmt = select(Product)

    if name is not None:
        stmt = stmt.where(Product.name.contains(name))

    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)

    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    if in_stock is not None:
        if in_stock:
            stmt = stmt.where(Product.stock > 0)
        else:
            stmt = stmt.where(Product.stock == 0)

    if sort == "price":
        stmt = stmt.order_by(Product.price)

    elif sort == "-price":
        stmt = stmt.order_by(Product.price.desc())

    elif sort == "name":
        stmt = stmt.order_by(Product.name)

    elif sort == "-name":
        stmt = stmt.order_by(Product.name.desc())

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt)

    stmt = stmt.offset(skip)
    stmt = stmt.limit(limit)

    Products = db.scalars(stmt).all()
    return Products, total


def update_product(db: Session, product: Product) -> Product:
    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
