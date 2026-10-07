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
