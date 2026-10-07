from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_admin_user
from app.db.database import get_db
from app.repositories import webhook_repository
from app.schemas.webhook import WebhookCreate, WebhookResponse

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
    dependencies=[Depends(get_admin_user)],
)


@router.post("", response_model=WebhookResponse)
def register_webhook(
    webhook: WebhookCreate,
    db: Session = Depends(get_db),
):
    return webhook_repository.create_webhook(db, str(webhook.url))


@router.get("", response_model=list[WebhookResponse])
def list_webhooks(
    db: Session = Depends(get_db),
):
    return webhook_repository.get_all_webhooks(db)


@router.delete("/{webhook_id}")
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
):
    success = webhook_repository.delete_webhook(db, webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"message": "Webhook deleted"}
