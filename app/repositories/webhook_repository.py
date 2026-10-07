from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.webhook import WebhookEndpoint


def create_webhook(db: Session, url: str) -> WebhookEndpoint:
    webhook = WebhookEndpoint(url=url)
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook


def get_active_webhooks(db: Session) -> list[WebhookEndpoint]:
    stmt = select(WebhookEndpoint).where(WebhookEndpoint.is_active == True)
    return list(db.scalars(stmt).all())


def get_all_webhooks(db: Session) -> list[WebhookEndpoint]:
    stmt = select(WebhookEndpoint).order_by(WebhookEndpoint.created_at.desc())
    return list(db.scalars(stmt).all())


def delete_webhook(db: Session, webhook_id: int) -> bool:
    stmt = select(WebhookEndpoint).where(WebhookEndpoint.id == webhook_id)
    webhook = db.scalars(stmt).first()
    if webhook:
        db.delete(webhook)
        db.commit()
        return True
    return False
