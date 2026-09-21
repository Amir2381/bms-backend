from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def create_category(db: Session, category: Category) -> Category:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> Category | None:
    stmt = select(Category).where(Category.id == category_id)
    return db.scalars(stmt).first()


def get_category_by_name(db: Session, name: str) -> Category | None:
    stmt = select(Category).where(Category.name == name)
    return db.scalars(stmt).first()


def get_all_categories(db: Session) -> list[Category]:
    stmt = select(Category).order_by(Category.name)
    return list(db.scalars(stmt).all())


def update_category(db: Session, category: Category) -> Category:
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
