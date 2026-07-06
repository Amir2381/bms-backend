from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    user = db.scalars(stmt).first()

    return user


def get_all_users(db: Session) -> list[User]:
    stmt = select(User)
    users = db.scalars(stmt).all()

    return users


def update_user(db: Session, user: User) -> User:
    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
