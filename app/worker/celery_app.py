from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "bms_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "check-at-risk-customers-midnight": {
        "task": "app.worker.tasks.check_at_risk_customers",
        "schedule": crontab(minute=0, hour=0),
    },
}
