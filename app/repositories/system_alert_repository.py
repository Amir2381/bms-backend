from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system_alert import SystemAlert


def get_all_alerts(
    db: Session, unread_only: bool = False, skip: int = 0, limit: int = 100
) -> list[SystemAlert]:
    stmt = select(SystemAlert).order_by(SystemAlert.created_at.desc())

    if unread_only:
        stmt = stmt.where(SystemAlert.is_read == False)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_alert(db: Session, alert_id: int) -> SystemAlert | None:
    stmt = select(SystemAlert).where(SystemAlert.id == alert_id)
    return db.scalars(stmt).first()


def mark_as_read(db: Session, alert: SystemAlert) -> SystemAlert:
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return alert
