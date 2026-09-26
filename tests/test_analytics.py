from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.models.category import Category
from app.models.product import Product
from app.models.sales import Sale, SaleItem
from app.models.branch import Branch
from tests.database import TestingSessionLocal


def test_get_summary_metrics(client: TestClient):
    db = TestingSessionLocal()

    sale1 = Sale(user_id=1, branch_id=1)
    sale2 = Sale(user_id=1, branch_id=1)
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
    assert response.status_code == 200, f"Expected 200, got {response.text}"

    data = response.json()
    assert float(data["total_sales"]) == 260.0
    assert data["total_transactions"] == 2
    assert float(data["average_order_value"]) == 130.0
    assert float(data["highest_sale"]) == 200.0
    assert float(data["lowest_sale"]) == 60.0
    assert data["sold_products_count"] == 6


def test_get_sales_trends(client: TestClient):
    db = TestingSessionLocal()

    sale1 = Sale(user_id=1, branch_id=1)
    sale2 = Sale(user_id=1, branch_id=1)
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
    assert response.status_code == 200, f"Expected 200, got {response.text}"

    data = response.json()
    assert "trends" in data
    assert isinstance(data["trends"], list)
    assert len(data["trends"]) >= 1

    trend = next((t for t in data["trends"] if t["date"] == sale_date), None)
    assert trend is not None
    assert float(trend["revenue"]) == 160.0
    assert trend["transaction_count"] == 2


def test_get_product_performance(client: TestClient):
    db = TestingSessionLocal()

    product2 = Product(name="Premium Mouse", price=25.0, stock=50)
    db.add(product2)
    db.commit()
    db.refresh(product2)

    sale1 = Sale(user_id=1, branch_id=1)
    db.add(sale1)
    db.commit()
    db.refresh(sale1)

    item1 = SaleItem(
        sale_id=sale1.id, product_id=1, quantity=2, unit_price=Decimal("50.0")
    )
    item2 = SaleItem(
        sale_id=sale1.id,
        product_id=product2.id,
        quantity=10,
        unit_price=Decimal("25.0"),
    )
    db.add_all([item1, item2])
    db.commit()

    product2_id = product2.id
    db.close()

    response = client.get("/analytics/products/performance?limit=10")
    assert response.status_code == 200, f"Expected 200, got {response.text}"

    data = response.json()
    assert "products" in data
    assert len(data["products"]) == 2

    top_product = data["products"][0]
    assert top_product["product_id"] == product2_id
    assert float(top_product["revenue"]) == 250.0
    assert 71.0 < float(top_product["revenue_share"]) < 72.0


def test_get_category_performance(client: TestClient):
    db = TestingSessionLocal()

    category = Category(name="Electronics")
    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(name="Smartphone", price=500.0, stock=10, category_id=category.id)
    db.add(product)
    db.commit()
    db.refresh(product)

    sale = Sale(user_id=1, branch_id=1)
    db.add(sale)
    db.commit()
    db.refresh(sale)

    item = SaleItem(
        sale_id=sale.id,
        product_id=product.id,
        quantity=2,
        unit_price=Decimal("450.0"),
    )
    db.add(item)
    db.commit()

    category_id = category.id
    db.close()

    response = client.get("/analytics/categories/performance?limit=10")
    assert response.status_code == 200, f"Expected 200, got {response.text}"

    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) >= 1

    target_category = next(
        (c for c in data["categories"] if c["category_id"] == category_id), None
    )

    assert target_category is not None
    assert float(target_category["revenue"]) == 900.0
    assert target_category["category_name"] == "Electronics"


def test_analytics_date_filtering(client: TestClient):
    db = TestingSessionLocal()

    sale_jan = Sale(
        user_id=1, branch_id=1, sale_date=datetime(2026, 1, 5, tzinfo=timezone.utc)
    )
    sale_feb = Sale(
        user_id=1, branch_id=1, sale_date=datetime(2026, 2, 10, tzinfo=timezone.utc)
    )
    db.add_all([sale_jan, sale_feb])
    db.commit()
    db.refresh(sale_jan)
    db.refresh(sale_feb)

    item_jan = SaleItem(
        sale_id=sale_jan.id, product_id=1, quantity=1, unit_price=Decimal("100.0")
    )
    item_feb = SaleItem(
        sale_id=sale_feb.id, product_id=1, quantity=2, unit_price=Decimal("200.0")
    )
    db.add_all([item_jan, item_feb])
    db.commit()
    db.close()

    response = client.get(
        "/analytics/metrics?start_date=2026-02-01&end_date=2026-02-28"
    )
    assert response.status_code == 200, f"Expected 200, got {response.text}"

    data = response.json()
    assert float(data["total_sales"]) == 400.0
    assert data["total_transactions"] == 1
    assert data["sold_products_count"] == 2


def test_analytics_branch_filtering_for_admin(client: TestClient):
    db = TestingSessionLocal()

    branch2 = Branch(name="Branch 2", location="Remote Area")
    db.add(branch2)
    db.commit()
    db.refresh(branch2)

    # Store ID before any session closing issues
    branch2_id = branch2.id

    sale1 = Sale(user_id=1, branch_id=1)
    sale2 = Sale(user_id=1, branch_id=branch2_id)
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
    db.close()

    response_all = client.get("/analytics/metrics")
    assert response_all.status_code == 200, f"Expected 200, got {response_all.text}"
    assert float(response_all.json()["total_sales"]) == 160.0

    response_b2 = client.get(f"/analytics/metrics?branch_id={branch2_id}")
    assert response_b2.status_code == 200, f"Expected 200, got {response_b2.text}"
    assert float(response_b2.json()["total_sales"]) == 60.0
