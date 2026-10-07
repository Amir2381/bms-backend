import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate


def create_api_key(db: Session, key_in: APIKeyCreate) -> APIKey:
    new_key = APIKey(
        name=key_in.name,
        key=secrets.token_urlsafe(32),
        scopes=key_in.scopes,
        expires_at=key_in.expires_at,
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key


def get_api_key_by_key(db: Session, key: str) -> APIKey | None:
    stmt = select(APIKey).where(APIKey.key == key)
    return db.scalars(stmt).first()


def get_api_key_by_id(db: Session, key_id: int) -> APIKey | None:
    stmt = select(APIKey).where(APIKey.id == key_id)
    return db.scalars(stmt).first()


def get_all_api_keys(db: Session) -> list[APIKey]:
    stmt = select(APIKey).order_by(APIKey.created_at.desc())
    return list(db.scalars(stmt).all())


def revoke_api_key(db: Session, key_record: APIKey) -> APIKey:
    key_record.is_active = False
    db.commit()
    db.refresh(key_record)
    return key_record
