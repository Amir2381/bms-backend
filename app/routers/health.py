import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.redis import sync_redis
from app.db.database import get_db
from app.worker.celery_app import celery_app

router = APIRouter(tags=["Health"])
logger = logging.getLogger("bms")


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    status_dict = {
        "status": "healthy",
        "services": {
            "database": "unhealthy",
            "redis": "unhealthy",
            "celery": "unhealthy",
        },
    }

    try:
        db.execute(text("SELECT 1"))
        status_dict["services"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status_dict["status"] = "unhealthy"

    try:
        if sync_redis.ping():
            status_dict["services"]["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        status_dict["status"] = "unhealthy"

    try:
        celery_ping = celery_app.control.ping(timeout=1.0)
        if celery_ping:
            status_dict["services"]["celery"] = "healthy"
        else:
            status_dict["services"]["celery"] = "unhealthy (no workers found)"
            status_dict["status"] = "unhealthy"
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        status_dict["status"] = "unhealthy"
        status_dict["services"]["celery"] = "unhealthy"

    return status_dict
