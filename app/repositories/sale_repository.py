from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.models.sales import Sale


def create_sale(db: Session, sale: Sale) -> Sale:
    db.add(sale)
    db.commit()
    db.refresh(sale)

    return sale


def get_sale(db: Session, sale_id: int) -> Sale | None:
    stmt = Select(Sale).where(Sale.id == sale_id)
    sale = db.scalars(stmt).first()

    return sale


def get_all_sales(db: Session) -> list[Sale]:
    stmt = Select(Sale)
    sales = db.scalars(stmt).all()

    return sales


def update_sale(db: Session, sale: Sale) -> Sale:
    db.commit()
    db.refresh(sale)

    return sale


def delete_sale(db: Session, sale: Sale) -> None:
    db.delete(sale)
    db.commit()
