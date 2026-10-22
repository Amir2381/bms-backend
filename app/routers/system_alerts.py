from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_admin_user
from app.db.database import get_db
from app.repositories import system_alert_repository
from app.schemas.system_alert import SystemAlertResponse

router = APIRouter(
    prefix="/alerts",
    tags=["System Alerts"],
    dependencies=[Depends(get_admin_user)],
)


@router.get("", response_model=list[SystemAlertResponse])
def get_alerts(
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return system_alert_repository.get_all_alerts(
        db, unread_only=unread_only, skip=skip, limit=limit
    )


@router.put("/{alert_id}/read", response_model=SystemAlertResponse)
def mark_alert_as_read(
    alert_id: int,
    db: Session = Depends(get_db),
):
    db_alert = system_alert_repository.get_alert(db, alert_id)
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return system_alert_repository.mark_as_read(db, db_alert)
