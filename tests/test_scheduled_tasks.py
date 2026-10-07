from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.models.customer import Customer
from app.models.sales import Sale, SaleItem
from app.models.system_alert import SystemAlert
from app.worker.tasks import check_at_risk_customers
from tests.database import TestingSessionLocal
from app.worker.celery_app import celery_app


def test_check_at_risk_customers_task():
    db = TestingSessionLocal()
    try:
        customer = Customer(phone="09999999999", full_name="At Risk Cust")
        db.add(customer)
        db.commit()
        db.refresh(customer)

        old_date = datetime.now(timezone.utc) - timedelta(days=95)
        sale = Sale(
            user_id=1,
            branch_id=1,
            customer_id=customer.id,
            sale_date=old_date,
            created_at=old_date,
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)

        item = SaleItem(
            sale_id=sale.id, product_id=1, quantity=1, unit_price=Decimal("100.0")
        )
        db.add(item)
        db.commit()

        check_at_risk_customers()

        alerts = (
            db.query(SystemAlert)
            .filter(SystemAlert.message.contains("At Risk Cust"))
            .all()
        )
        assert len(alerts) == 1
        assert alerts[0].type == "WARNING"

        check_at_risk_customers()

        alerts_after = (
            db.query(SystemAlert)
            .filter(SystemAlert.message.contains("At Risk Cust"))
            .all()
        )
        assert len(alerts_after) == 1

    finally:
        db.close()


def test_celery_beat_schedule_configured():
    schedule = celery_app.conf.beat_schedule
    assert "check-at-risk-customers-midnight" in schedule
    task_info = schedule["check-at-risk-customers-midnight"]
    assert task_info["task"] == "app.worker.tasks.check_at_risk_customers"
