from decimal import Decimal

from fastapi.testclient import TestClient

from app.models.sales import Sale, SaleItem
from tests.database import TestingSessionLocal


def test_get_summary_metrics(client: TestClient):
    db = TestingSessionLocal()

    sale1 = Sale(user_id=1)
    sale2 = Sale(user_id=1)
    db.add_all([sale1, sale2])
    db.commit()
    db.refresh(sale1)
    db.refresh(sale2)

    item1 = SaleItem(
        sale_id=sale1.id, product_id=1, quantity=2, unit_price=Decimal("50.0")
    )
    item2 = SaleItem(
        sale_id=sale1.id, product_id=1, quantity=1, unit_price=Decimal("100.0")
    )
    item3 = SaleItem(
        sale_id=sale2.id, product_id=1, quantity=3, unit_price=Decimal("20.0")
    )

    db.add_all([item1, item2, item3])
    db.commit()
    db.close()

    response = client.get("/analytics/metrics")
    assert response.status_code == 200

    data = response.json()
    assert float(data["total_sales"]) == 260.0
    assert data["total_transactions"] == 2
    assert float(data["average_order_value"]) == 130.0
    assert float(data["highest_sale"]) == 200.0
    assert float(data["lowest_sale"]) == 60.0
    assert data["sold_products_count"] == 6


def test_get_sales_trends(client: TestClient):
    db = TestingSessionLocal()

    sale1 = Sale(user_id=1)
    sale2 = Sale(user_id=1)
    db.add_all([sale1, sale2])
    db.commit()
    db.refresh(sale1)
    db.refresh(sale2)

    item1 = SaleItem(
        sale_id=sale1.id, product_id=1, quantity=2, unit_price=Decimal("50.0")
    )
    item2 = SaleItem(
        sale_id=sale2.id, product_id=1, quantity=3, unit_price=Decimal("20.0")
    )
    db.add_all([item1, item2])
    db.commit()

    db.refresh(sale1)
    sale_date = sale1.sale_date.date().isoformat()

    db.close()

    response = client.get("/analytics/trends?period=daily")
    assert response.status_code == 200

    data = response.json()
    assert "trends" in data
    assert isinstance(data["trends"], list)
    assert len(data["trends"]) >= 1

    trend = next((t for t in data["trends"] if t["date"] == sale_date), None)
    assert trend is not None
    assert float(trend["revenue"]) == 160.0
    assert trend["transaction_count"] == 2
