import json
import socket
import urllib.request
from urllib.error import URLError, HTTPError
from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.system_alert import SystemAlert
from app.repositories import sale_repository
from app.worker.celery_app import celery_app


@celery_app.task
def check_and_create_alerts(branch_id: int):
    with SessionLocal() as db:
        alerts_data = sale_repository.get_inventory_alerts(
            db, days_threshold=3, lookback_days=30, branch_id=branch_id
        )
        for alert in alerts_data:
            if alert["current_stock"] == 0:
                alert_type = "CRITICAL"
                msg = f"Product '{alert['product_name']}' is out of stock!"
            else:
                alert_type = "WARNING"
                msg = f"Product '{alert['product_name']}' will run out in ~{round(alert['days_remaining'])} days."

            new_alert = SystemAlert(
                branch_id=branch_id,
                type=alert_type,
                message=msg,
            )
            db.add(new_alert)
        db.commit()


@celery_app.task
def check_at_risk_customers():
    with SessionLocal() as db:
        rfm_data = sale_repository.get_rfm_data(db, limit=1000)

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)

        for item in rfm_data:
            r = item["recency_days"]
            f = item["frequency"]

            if r > 90 and f < 2:
                customer_name = item["customer_name"]
                msg = f"Customer '{customer_name}' has reached the 'At Risk' segment."

                stmt = select(SystemAlert).where(
                    SystemAlert.message == msg, SystemAlert.created_at >= cutoff_date
                )
                existing_alert = db.scalars(stmt).first()

                if not existing_alert:
                    new_alert = SystemAlert(
                        branch_id=None,
                        type="WARNING",
                        message=msg,
                    )
                    db.add(new_alert)

        db.commit()


@celery_app.task(bind=True, max_retries=5)
def send_webhook_event(self, url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status
    except (URLError, HTTPError, socket.timeout) as exc:
        countdown = 2 ** (self.request.retries + 1)
        raise self.retry(exc=exc, countdown=countdown)
