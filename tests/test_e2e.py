from io import BytesIO

from tests.database import TestingSessionLocal
from app.models.audit_log import AuditLog


def test_end_to_end_import_to_analytics(client):
    category_response = client.post("/categories", json={"name": "E2E Category"})
    assert category_response.status_code == 200
    category_id = category_response.json()["id"]

    product_response = client.post(
        "/products",
        json={
            "name": "E2E Product",
            "price": 100.0,
            "stock": 50,
            "category_id": category_id,
        },
    )
    assert product_response.status_code == 200

    csv_content = "date,product,quantity,unit_price\n2026-10-01,E2E Product,2,90.00\n"
    import_response = client.post(
        "/import/sales",
        files={
            "file": (
                "e2e_sales.csv",
                BytesIO(csv_content.encode("utf-8")),
                "text/csv",
            )
        },
    )
    assert import_response.status_code == 200
    assert import_response.json()["imported_rows"] == 1

    metrics_response = client.get("/analytics/metrics")
    assert metrics_response.status_code == 200
    metrics_data = metrics_response.json()
    assert float(metrics_data["total_sales"]) >= 180.0

    visualizations_response = client.get("/analytics/visualizations/sales-distribution")
    assert visualizations_response.status_code == 200
    vis_data = visualizations_response.json()
    assert "E2E Category" in vis_data["category_distribution"]["labels"]

    db = TestingSessionLocal()
    try:
        log = db.query(AuditLog).filter(AuditLog.action == "IMPORT_SALES").first()
        assert log is not None
        assert log.details["imported_rows"] >= 1
    finally:
        db.close()
