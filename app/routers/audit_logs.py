from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_admin_user
from app.db.database import get_db
from app.repositories import audit_log_repository
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
    dependencies=[Depends(get_admin_user)],
)


@router.get("", response_model=list[AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return audit_log_repository.get_all_audit_logs(db, skip=skip, limit=limit)
