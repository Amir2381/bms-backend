from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer


def create_customer(db: Session, customer: Customer) -> Customer:
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: int) -> Customer | None:
    stmt = select(Customer).where(Customer.id == customer_id)
    return db.scalars(stmt).first()


def get_customer_by_phone(db: Session, phone: str) -> Customer | None:
    stmt = select(Customer).where(Customer.phone == phone)
    return db.scalars(stmt).first()


def get_all_customers(db: Session) -> list[Customer]:
    stmt = select(Customer).order_by(Customer.created_at.desc())
    return list(db.scalars(stmt).all())
