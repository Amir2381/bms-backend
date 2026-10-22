from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def get_all_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> list[AuditLog]:
    stmt = (
        select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
    )
    return list(db.scalars(stmt).all())
